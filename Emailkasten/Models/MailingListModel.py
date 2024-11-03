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

from .CorrespondentModel import CorrespondentModel


class MailingListModel(models.Model):
    """Database model for a mailinglist."""

    list_id = models.CharField(max_length=255)
    """The List-ID header of the mailinglist. Unique together with `correspondent`."""

    list_owner = models.CharField(max_length=255, null=True)
    """The List-Owner header of the mailinglist. Can be null."""

    list_subscribe = models.EmailField(max_length=255, null=True)
    """The List-Subscribe header of the mailinglist. Can be null."""

    list_unsubscribe = models.EmailField(max_length=255, null=True)
    """The List-Unsubscribe header of the mailinglist. Can be null."""

    list_post = models.CharField(max_length=255, null=True)
    """The List-Post header of the mailinglist. Can be null."""

    list_help = models.CharField(max_length=255, null=True)
    """The List-Help header of the mailinglist. Can be null."""

    list_archive = models.CharField(max_length=255, null=True)
    """The List-Archive header of the mailinglist. Can be null."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailingslists. False by default."""

    correspondent = models.ForeignKey(CorrespondentModel, related_name='mailinglist', on_delete=models.CASCADE)
    """The correspondent that sends the mailinglist. Unique together with `list_id`. Deletion of that `correspondent` deletes this mailinglist."""
    
    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Mailinglist {self.list_id}"

    class Meta:
        db_table = "mailinglists"
        """The name of the database table for the mailinglists."""

        unique_together = ("list_id", "correspondent")
        """`list_id` and `correspondent` in combination are unique."""


