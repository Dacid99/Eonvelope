'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from django.db import models
from .EMailModel import EMailModel
from .. import constants

class AttachmentModel(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=511,
        recursive=True,
        null=True)
    datasize = models.IntegerField()
    email = models.ForeignKey(EMailModel, related_name="attachments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment {self.file_name}"

    class Meta:
        db_table = "attachments"
        unique_together = ("file_path", "email")

