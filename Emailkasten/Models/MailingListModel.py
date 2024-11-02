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
from rest_framework.decorators import action
from .CorrespondentModel import CorrespondentModel

class MailingListModel(models.Model):
    list_id = models.CharField(max_length=255)
    list_owner = models.CharField(max_length=255, null=True)
    list_subscribe = models.EmailField(max_length=255, null=True)
    list_unsubscribe = models.EmailField(max_length=255, null=True)
    list_post = models.CharField(max_length=255, null=True)
    list_help = models.CharField(max_length=255, null=True)
    list_archive = models.CharField(max_length=255, null=True)
    is_favorite = models.BooleanField(default=False)
    correspondent = models.ForeignKey(CorrespondentModel, related_name='mailinglist', on_delete=models.CASCADE)

    
    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Mailinglist {self.list_id}"

    class Meta:
        db_table = "mailinglists"
        unique_together = ("list_id", "correspondent")

