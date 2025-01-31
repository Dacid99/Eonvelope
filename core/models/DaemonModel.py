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

"""Module with the :class:`DaemonModel` model class."""

import logging
import os
import uuid

from Emailkasten.utils import get_config
from dirtyfields import DirtyFieldsMixin
from django.db import models

import Emailkasten.constants

from .. import constants
from .MailboxModel import MailboxModel

logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class DaemonModel(DirtyFieldsMixin, models.Model):
    """Database model for the daemon fetching a mailbox."""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    """The uuid of this daemon. Used to create a unique logfile."""

    mailbox = models.ForeignKey(MailboxModel, related_name='daemons', on_delete=models.CASCADE)
    """The mailbox this daemon fetches. Unique. Deletion of that :attr:`mailbox` deletes this daemon."""

    FETCHINGCHOICES = list(constants.MailFetchingCriteria())
    """The available mail fetching criteria. Refers to :class:`Emailkasten.constants.MailFetchingCriteria`."""

    fetching_criterion = models.CharField(choices=FETCHINGCHOICES, default=constants.MailFetchingCriteria.ALL, max_length=10)
    """The fetching criterion for this mailbox. One of :attr:`FETCHING_CHOICES`. :attr:`Emailkasten.constants.MailFetchingCriteria.ALL` by default."""

    cycle_interval = models.IntegerField(default=get_config('DAEMON_CYCLE_PERIOD_DEFAULT'))
    """The period with which the daemon is running. :attr:`constance.get_config('DAEMON_CYCLE_PERIOD_DEFAULT')` by default."""

    restart_time = models.IntegerField(default=get_config('DAEMON_RESTART_TIME_DEFAULT'))
    """The time after which a crashed daemon restarts. :attr:`constance.get_config('DAEMON_RESTART_TIME_DEFAULT')` by default."""

    is_running = models.BooleanField(default=False)
    """Flags whether the daemon is active. `False` by default.

    Important:
        This must only be changed by internal mechanism, never by the user!
    """

    is_healthy = models.BooleanField(default=True)
    """Flags whether the daemon is healthy. `True` by default."""

    log_filepath = models.FilePathField(
        path=Emailkasten.constants.LoggerConfiguration.LOG_DIRECTORY_PATH,
        recursive=True,
        unique=True)
    """The logfile the daemon logs to. Is automatically set by :func:`save`. Unique."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Mailfetcher daemon configuration {str(self.uuid)} for mailbox {self.mailbox}"


    class Meta:
        """Metadata class for the model."""

        db_table = 'daemons'
        """The name of the database table for the daemons."""


    def save(self, *args, **kwargs):
        """Extended :django::func:`django.models.Model.save` method to create and set :attr:`log_filepath` if it is null."""

        if not self.log_filepath:
            self.log_filepath = os.path.join(Emailkasten.constants.LoggerConfiguration.LOG_DIRECTORY_PATH, f"daemon_{self.uuid}.log")
            if not os.path.exists(self.log_filepath):
                with open(self.log_filepath, 'w'):
                    pass
        super().save(*args,**kwargs)
