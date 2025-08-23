# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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
from typing import TYPE_CHECKING, Any, Final, override

from celery import current_app
from dirtyfields import DirtyFieldsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from ..constants import EmailFetchingCriterionChoices
from ..mixins import URLMixin


if TYPE_CHECKING:
    from .Mailbox import Mailbox


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Daemon(DirtyFieldsMixin, URLMixin, models.Model):
    """Database model for the daemon fetching a mailbox."""

    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("UUID"),
    )
    """The uuid of this daemon. Used to create a unique logfile."""

    mailbox: models.ForeignKey[Mailbox] = models.ForeignKey(
        "Mailbox",
        related_name="daemons",
        on_delete=models.CASCADE,
        verbose_name=_("mailbox"),
    )
    """The mailbox this daemon fetches. Unique. Deletion of that :attr:`mailbox` deletes this daemon."""

    fetching_criterion = models.CharField(
        choices=EmailFetchingCriterionChoices.choices,
        default=EmailFetchingCriterionChoices.ALL,
        max_length=127,
        verbose_name=_("fetching criterion"),
        help_text=_("The selection criterion for emails to archive."),
    )
    """The fetching criterion for this mailbox. :attr:`Emailkasten.constants.EmailFetchingCriterionChoices.ALL` by default."""

    celery_task: models.OneToOneField[PeriodicTask] = models.OneToOneField(
        PeriodicTask,
        on_delete=models.CASCADE,
        null=True,
        verbose_name=_("celery task"),
    )
    """The periodic celery task wrapped by this daemon."""

    interval: models.ForeignKey[IntervalSchedule] = models.ForeignKey(
        IntervalSchedule,
        on_delete=models.PROTECT,
        verbose_name=_("interval"),
        help_text=_("The time between two daemon runs in seconds."),
    )
    """The period with which the daemon is running."""

    is_healthy = models.BooleanField(
        null=True,
        verbose_name=_("healthy"),
    )
    """Flags whether the daemon is healthy. `None` by default.
    When the :attr:`core.models.Mailbox.is_healthy` field changes to `False`, this field is updated accordingly.
    When this field changes to `True`, the :attr:`core.models.Mailbox.is_healthy` field of :attr:`mailbox` will be set to `True` as well by a signal.
    """

    last_error = models.TextField(
        blank=True,
        default="",
        verbose_name=_("last error"),
    )
    """The error from the most recent failed task execution."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created"),
    )
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("last updated"),
    )
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "daemon"

    DELETE_NOTICE = _("This will only delete this daemon, not its mailbox.")

    class Meta:
        """Metadata class for the model."""

        db_table = "daemons"
        """The name of the database table for the daemons."""

        constraints: Final[list[models.BaseConstraint]] = [
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
        return _("Emailfetcherdaemon %(uuid)s for mailbox %(mailbox)s") % {
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
        logger.info("Testing daemon %s ...", self)

        daemon_task = self.celery_task.task
        args = json.loads(self.celery_task.args or "[]")
        kwargs = json.loads(self.celery_task.kwargs or "{}")
        try:
            current_app.send_task(daemon_task, args=args, kwargs=kwargs).get()
        except Exception:
            logger.exception("Failed testing daemon %s!", self)
            raise
        logger.info("Successfully tested daemon %s ...", self)

    def start(self) -> bool:
        """Start the daemons :attr:`celery_task`.

        Returns:
            Whether the start operation was successful.
        """
        logger.debug("Starting %s ...", self)
        if not self.celery_task.enabled:
            self.celery_task.enabled = True
            self.celery_task.save(update_fields=["enabled"])
            logger.debug("Successfully started daemon.")
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
            logger.debug("Successfully stopped daemon.")
            return True
        logger.debug("%s was not running.", self)
        return False
