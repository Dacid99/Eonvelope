# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from django.db import models

from .. import constants
from .MailboxModel import MailboxModel


class DaemonModel(models.Model):
    """Database model for the daemon fetching a mailbox."""

    mailbox = models.OneToOneField(MailboxModel, related_name='daemon', on_delete=models.CASCADE)
    """The mailbox this daemon fetches. Unique. Deletion of that `mailbox` deletes this daemon."""

    cycle_interval = models.IntegerField(default=constants.EMailArchiverDaemonConfiguration.CYCLE_PERIOD_DEFAULT)
    """The interval in which the mailbox is fetched. Set to :attr:`Emailkasten.constants.EMailArchiverDaemonConfiguration.CYCLE_PERIOD_DEFAULT` by default."""
    
    is_running = models.BooleanField(default=False)
    """Flags whether the daemon is active. `False` by default."""
    
    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""
    

    class Meta:
        db_table = 'daemons'
        """The name of the database table for the daemons."""

        
    def __str__(self):
        return f"Mailfetcher daemon configuration for mailbox {self.mailbox}"
    
