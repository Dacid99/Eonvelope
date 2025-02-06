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

"""Module with the :class:`ImageModel` model class."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from django.db import models

from Emailkasten.utils import get_config

from ..utils.fileManagment import saveStore
from .StorageModel import StorageModel

if TYPE_CHECKING:
    from email.message import Message
    from io import BufferedWriter
    from typing import Any, Callable

    from .EMailModel import EMailModel

logger = logging.getLogger(__name__)


class ImageModel(models.Model):
    """Database model for an image in a mail."""

    file_name = models.CharField(max_length=255)
    """The filename of the image."""

    file_path = models.FilePathField(
        path=get_config("STORAGE_PATH"), max_length=511, recursive=True, null=True
    )
    """The path where the image is stored. Unique together with :attr:`email`.
    Can be null if the image has not been saved (null does not collide with the unique constraint.).
    Must contain :attr:`constance.get_config('STORAGE_PATH')`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_ImageModel.post_delete_image`."""

    datasize = models.IntegerField()
    """The filesize of the image."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite images. False by default."""

    email: models.ForeignKey[EMailModel] = models.ForeignKey(
        "EMailModel", related_name="images", on_delete=models.CASCADE
    )
    """The mail that the image was found in. Deletion of that `email` deletes this image."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Image {self.file_name} from {str(self.email)}"

    class Meta:
        """Metadata class for the model."""

        db_table = "images"
        """The name of the database table for the images."""

        constraints = [
            models.UniqueConstraint(
                fields=["file_path", "email"],
                name="image_unique_together_file_path_email",
            )
        ]
        """:attr:`file_path` and :attr:`email` in combination are unique."""

    def delete(self, *args, **kwargs):
        """Extended :django::func:`django.models.Model.delete` method to delete :attr:`file_path` file on deletion."""
        super().delete(*args, **kwargs)

        if self.file_path:
            logger.debug("Removing %s from storage ...", str(self))
            try:
                os.remove(self.file_path)
                logger.debug(
                    "Successfully removed the image file from storage.", exc_info=True
                )
            except FileNotFoundError:
                logger.error("%s was not found!", self.file_path, exc_info=True)
            except OSError:
                logger.error(
                    "An OS error occured removing %s!", self.file_path, exc_info=True
                )
            except Exception:
                logger.error(
                    "An unexpected error occured removing %s!",
                    self.file_path,
                    exc_info=True,
                )

    def save(self, *args, **kwargs):
        """Extended :django::func:`django.models.Model.save` method
        to save the data to storage if configured.
        """
        super().save(*args, **kwargs)
        if "imageData" in kwargs and get_config("SAVE_IMAGES"):
            self.save_to_storage(kwargs["imageData"])

    def save_to_storage(self, imageData: Message[str, str]):
        """Saves the image file to the storage.
        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.fileManagment.saveStore` to wrap the storing process.

        Args:
            imageData: The data of the image to be saved.
        """
        if self.file_path:
            logger.debug("%s is already stored.", self)
            return

        @saveStore
        def writeImage(file: BufferedWriter, imageData: Message[str, str]):
            file.write(imageData.get_payload(decode=True))

        logger.debug("Storing image %s ...", self)

        dirPath = StorageModel.getSubdirectory(self.email.message_id)
        preliminary_file_path = os.path.join(dirPath, self.file_name)

        self.file_path = writeImage(preliminary_file_path, imageData)
        self.save(update_fields=["file_path"])

        logger.debug("Successfully stored image.")

    @staticmethod
    def fromData(imageData: Message[str, str], email=None) -> ImageModel:
        new_image = ImageModel()

        new_image.file_name = imageData.get_filename()
        new_image.datasize = len(imageData.as_bytes())
        new_image.email = email

        return new_image
