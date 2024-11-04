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

from ..constants import ParsedMailKeys
from .CorrespondentModel import CorrespondentModel
from .EMailModel import EMailModel


class EMailCorrespondentsModel(models.Model):
    """Database model for connecting emails and their correspondents."""

    email = models.ForeignKey(EMailModel, related_name="emailcorrespondents", on_delete=models.CASCADE)
    """The email :attr:`correspondent` was mentioned in. Unique together with :attr:`correspondent` and :attr:`mention`."""

    correspondent = models.ForeignKey(CorrespondentModel, related_name="correspondentemails", on_delete=models.CASCADE)
    """The correspondent that was mentioned in :attr:`email`. Unique together with :attr:`email` and :attr:`mention`."""

    MENTIONTYPES = dict(ParsedMailKeys.Correspondent())
    """The available types of correspondent memtions. Refers to :class:`Emailkasten.constants.ParsedMailKeys.Correspondent`."""

    mention = models.CharField(choices=MENTIONTYPES, max_length=30)
    """The way that :attr:`correspondent` was mentioned in :attr:`email`. One of :attr:`MENTIONTYPES`.  Unique together with :attr:`email` and :attr:`correspondent`."""
    
    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"EMail-Correspondent connection from email {self.email} to correspondent {self.correspondent} with mention {self.mention}"
    
    class Meta:
        db_table = "email_correspondents"
        """The name of the database table for the images."""

        unique_together = ('email', 'correspondent', 'mention')
        """:attr:`email`, :attr:`correspondent` and :attr:`mention` in combination are unique."""