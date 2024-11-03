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
from .EMailModel import EMailModel


class ImageModel(models.Model):
    """Database model for an image in a mail."""

    file_name = models.CharField(max_length=255)
    """The filename of the image."""

    file_path = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=511,
        recursive=True,
        null=True)
    """The path where the image is stored. Unique together with `email`.
    Can be null if the image has not been saved (null does not collide with the unique constraint.).
    Must contain :attr:`Emailkasten.constants.StorageConfiguration.STORAGE_PATH`."""

    datasize = models.IntegerField()
    """The filesize of the image."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite images. False by default."""

    email = models.ForeignKey(EMailModel, related_name="images", on_delete=models.CASCADE)
    """The mail that the image was found in. Deletion of that `email` deletes this image."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""


    def __str__(self):
        return f"Image {self.file_name}"

    class Meta:
        db_table = "images"
        """The name of the database table for the images."""

        unique_together = ("file_path", "email")
        """`file_path` and `email` in combination are unique."""
