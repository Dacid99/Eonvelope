# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
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
import logging.handlers
import os
import uuid
from functools import cached_property
from typing import TYPE_CHECKING, Any, Final, override

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from Emailkasten.utils.workarounds import get_config

from ..constants import EmailFetchingCriterionChoices
from ..mixins import HasDownloadMixin, URLMixin


if TYPE_CHECKING:
    from .Mailbox import Mailbox


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Daemon(DirtyFieldsMixin, HasDownloadMixin, URLMixin, models.Model):
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

    interval: models.ForeignKey[IntervalSchedule] = models.ForeignKey(
        IntervalSchedule,
        on_delete=models.PROTECT,
        verbose_name=_("interval"),
        help_text=_("The time between two daemon runs in seconds."),
    )
    """The period with which the daemon is running. :attr:`constance.config('DAEMON_CYCLE_PERIOD_DEFAULT')` by default."""

    is_healthy = models.BooleanField(
        null=True,
        verbose_name=_("healthy"),
    )
    """Flags whether the daemon is healthy. `None` by default.
    When the :attr:`core.models.Mailbox.is_healthy` field changes to `False`, this field is updated accordingly.
    When this field changes to `True`, the :attr:`core.models.Mailbox.is_healthy` field of :attr:`mailbox` will be set to `True` as well by a signal.
    """

    log_filepath = models.FilePathField(
        path=str(settings.LOG_DIRECTORY_PATH),
        recursive=True,
        unique=True,
        verbose_name=_("logfilepath"),
    )
    """The logfile the daemon logs to. Is automatically set by :func:`save`. Unique."""

    log_backup_count = models.PositiveSmallIntegerField(
        default=get_config("DAEMON_LOG_BACKUP_COUNT_DEFAULT"),
        verbose_name=_("logfile backup count"),
        help_text=_("The number of historical logfiles to keep."),
    )
    """The number of backup logfiles for the daemon. :attr:`constance.config('DAEMON_LOG_BACKUP_COUNT_DEFAULT')` by default."""

    logfile_size = models.PositiveIntegerField(
        default=get_config("DAEMON_LOGFILE_SIZE_DEFAULT"),
        verbose_name=_("logfile maximum size"),
        help_text=_("The maximum size of a logfile in bytes."),
    )
    """The maximum size of a logfile for the daemon in bytes. :attr:`constance.config('DAEMON_LOGFILE_SIZE_DEFAULT')` by default."""

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
        """Extended :django::func:`django.models.Model.save` method.

        Create and sets :attr:`log_filepath` if it is null.
        """
        if not self.log_filepath:
            self.setup_logger()  # Order may be crucial here to set the logger up before its used
        if not self.pk:
            self.celery_task = PeriodicTask.objects.create(
                interval=self.interval,
                name=str(self.uuid),
                task="core.tasks.fetch_emails",
                args=json.dumps([str(self.uuid)]),
            )
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
            if (
                self.fetching_criterion
                not in self.mailbox.get_available_fetching_criteria()
            ):
                raise ValidationError(
                    {
                        "fetching_criterion": "This fetching criterion is not available for this mailbox!"
                    }
                )
        except Daemon.mailbox.RelatedObjectDoesNotExist:
            raise ValidationError({"mailbox": "No valid mailbox selected!"}) from None

    def setup_logger(self) -> None:
        """Sets up the logger for the daemon process."""
        daemon_logger = logging.getLogger(str(self.uuid))
        self.log_filepath = os.path.join(
            settings.LOG_DIRECTORY_PATH,
            f"{daemon_logger.name}.log",
        )
        file_handler = logging.handlers.RotatingFileHandler(
            filename=self.log_filepath,
            backupCount=self.log_backup_count,
            maxBytes=self.logfile_size,
        )
        file_handler.setFormatter(logging.Formatter(settings.LOGFORMAT, style="{"))
        daemon_logger.addHandler(file_handler)

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

    @override
    @cached_property
    def has_download(self) -> bool:
        """Daemon always has a logfile."""
        return self.log_filepath is not None

    @override
    def get_absolute_download_url(self) -> str:
        """Returns the url of the log download api endpoint."""
        return reverse(f"api:v1:{self.BASENAME}-log-download", kwargs={"pk": self.pk})
