# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`Daemon` model class."""

from __future__ import annotations

import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, ClassVar, override

from celery import current_app
from dirtyfields import DirtyFieldsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django_prometheus.models import ExportModelOperationsMixin

from core.constants import EmailFetchingCriterionChoices
from core.mixins import HealthModelMixin, TimestampModelMixin, URLMixin


if TYPE_CHECKING:
    from .Mailbox import Mailbox


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Daemon(
    ExportModelOperationsMixin("routine"),
    DirtyFieldsMixin,
    URLMixin,
    HealthModelMixin,
    TimestampModelMixin,
    models.Model,
):
    """Database model for the daemon fetching a mailbox.

    Note:
        The internal name of this object is ``daemon``, the external name for the user interface is ``routine``.
    """

    BASENAME = "daemon"

    DELETE_NOTICE = _("This will only delete this routine, not its mailbox.")

    DELETE_NOTICE_PLURAL = _(
        "This will only delete these routine, not their mailboxes."
    )

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("UUID"),
    )
    """The uuid of this daemon. Used to create a unique logfile."""

    mailbox: models.ForeignKey[Mailbox] = models.ForeignKey(
        "Mailbox",
        related_name="daemons",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("mailbox"),
    )
    """The mailbox this daemon fetches. Unique. Deletion of that :attr:`mailbox` deletes this daemon."""

    fetching_criterion = models.CharField(
        choices=EmailFetchingCriterionChoices.choices,
        default=EmailFetchingCriterionChoices.ALL,
        max_length=127,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("fetching criterion"),
        help_text=_("The selection criterion for emails to archive."),
    )
    """The fetching criterion for this mailbox. :attr:`eonvelope.constants.EmailFetchingCriterionChoices.ALL` by default."""

    celery_task: models.OneToOneField[PeriodicTask] = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        null=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("celery task"),
    )
    """The periodic celery task wrapped by this daemon."""

    interval: models.ForeignKey[IntervalSchedule] = models.ForeignKey(
        IntervalSchedule,
        on_delete=models.PROTECT,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("interval"),
        help_text=_("The time between two routine runs in seconds."),
    )
    """The period with which the daemon is running."""

    class Meta:
        """Metadata class for the model."""

        db_table = "daemons"
        """The name of the database table for the daemons."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("routine")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("routines")
        get_latest_by = TimestampModelMixin.Meta.get_latest_by

        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.CheckConstraint(
                condition=models.Q(
                    fetching_criterion__in=EmailFetchingCriterionChoices.values
                ),
                name="fetching_criterion_valid_choice",
            ),
            models.UniqueConstraint(
                fields=["mailbox", "fetching_criterion"],
                name="daemon_unique_together_mailbox_fetching_criterion",
            ),
        ]
        """Choices for :attr:`fetching_criterion` are enforced on db level.
        :attr:`fetching_criterion` and :attr:`mailbox` are unique together.
        """

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the daemon, using :attr:`uuid` and :attr:`mailbox`.
        """
        return _("Emailfetching routine %(uuid)s for mailbox %(mailbox)s") % {
            "uuid": self.uuid,
            "mailbox": self.mailbox,
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method."""
        if not self.pk:
            self.celery_task = PeriodicTask.objects.create(
                interval=self.interval,
                name=str(self.uuid),
                task="core.tasks.fetch_emails",
                args=json.dumps([str(self.uuid)]),
            )
        else:
            self.celery_task.interval = self.interval
            self.celery_task.save()
        super().save(*args, **kwargs)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        if self.celery_task is not None:
            self.celery_task.delete()
        return super().delete(*args, **kwargs)

    @override
    def clean(self) -> None:
        """Validates that :attr:`fetching_criterion` is available for the :attr:`mailbox.account`."""
        try:
            if self.fetching_criterion not in self.mailbox.available_fetching_criteria:
                raise ValidationError(
                    {
                        "fetching_criterion": _(
                            "This fetching criterion is not available for this mailbox!"
                        )
                    }
                )
        except Daemon.mailbox.RelatedObjectDoesNotExist:
            raise ValidationError(
                {"mailbox": _("No valid mailbox selected!")}
            ) from None

    def test(self) -> None:
        """Tests whether the data in the model is correct and the daemons task can be run.

        Tests the entire task, including fetching and the celery backend.
        The :attr:`core.models.Daemon.is_healthy` flag is set accordingly by the task itself.

        Raises:
            Exception: Any exception raised by the task.
        """
        logger.info("Testing routine %s ...", self)

        daemon_task = self.celery_task.task
        args = json.loads(self.celery_task.args or "[]")
        kwargs = json.loads(self.celery_task.kwargs or "{}")
        try:
            current_app.send_task(daemon_task, args=args, kwargs=kwargs).get()
        except Exception:
            logger.exception("Failed testing routine %s!", self)
            raise
        logger.info("Successfully tested routine %s ...", self)

    def start(self) -> bool:
        """Start the daemons :attr:`celery_task`.

        Returns:
            Whether the start operation was successful.
        """
        logger.debug("Starting %s ...", self)
        if not self.celery_task.enabled:
            self.celery_task.enabled = True
            self.celery_task.save(update_fields=["enabled"])
            logger.debug("Successfully started routine.")
            return True
        logger.debug("%s was already running.", self)
        return False

    def stop(self) -> bool:
        """Stops the daemons :attr:`celery_task`.

        Returns:
            Whether the stop operation was successful.
        """
        logger.debug("Stopping %s ...", self)
        if self.celery_task.enabled:
            self.celery_task.enabled = False
            self.celery_task.save(update_fields=["enabled"])
            logger.debug("Successfully stopped routine.")
            return True
        logger.debug("%s was not running.", self)
        return False
