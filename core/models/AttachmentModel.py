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

"""Module with the :class:`AttachmentModel` model class."""

from __future__ import annotations

import logging
import os
from hashlib import md5
from typing import TYPE_CHECKING, Any, Final, override

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.mixins.HasDownloadMixin import HasDownloadMixin
from core.mixins.HasThumbnailMixin import HasThumbnailMixin
from core.mixins.URLMixin import URLMixin
from Emailkasten.utils import get_config

from ..utils.fileManagment import clean_filename, saveStore
from .StorageModel import StorageModel


if TYPE_CHECKING:
    from email.message import Message
    from io import BufferedWriter

    from .EMailModel import EMailModel


logger = logging.getLogger(__name__)


class AttachmentModel(HasDownloadMixin, HasThumbnailMixin, URLMixin, models.Model):
    """Database model for an attachment file in a mail."""

    file_name = models.CharField(max_length=255)
    """The filename of the attachment."""

    file_path = models.FilePathField(
        path=get_config("STORAGE_PATH"), max_length=511, recursive=True, null=True
    )
    """The path where the attachment is stored. Unique together with :attr:`email`.
    Can be null if the attachment has not been saved (null does not collide with the unique constraint.).
    Must contain :attr:`constance.get_config('STORAGE_PATH')`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_AttachmentModel.post_delete_attachment`."""

    content_disposition = models.CharField(blank=True, default="", max_length=255)
    """The disposition of the file. Typically 'attachment', 'inline' or ''."""

    content_type = models.CharField(max_length=255, default="")
    """The type of the file."""

    datasize = models.PositiveIntegerField()
    """The filesize of the attachment."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite attachments. False by default."""

    email: models.ForeignKey[EMailModel] = models.ForeignKey(
        "EMailModel", related_name="attachments", on_delete=models.CASCADE
    )
    """The mail that the attachment was found in.  Deletion of that `email` deletes this attachment."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "attachment"

    DELETE_NOTICE = _("This will only delete this attachment, not the email.")

    class Meta:
        """Metadata class for the model."""

        db_table = "attachments"
        """The name of the database table for the attachments."""

        constraints: Final[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["file_path", "email"],
                name="attachment_unique_together_file_path_email",
            )
        ]
        """:attr:`file_path` and :attr:`email` in combination are unique."""

    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the attachment, using :attr:`file_name` and :attr:`email`.
        """
        return _("Attachment %(file_name)s from %(email)s") % {
            "file_name": self.file_name,
            "email": self.email,
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method.

        Cleans the filename.
        Saves the data to storage if configured.
        """
        self.file_name = clean_filename(self.file_name)
        attachmentData = kwargs.pop("attachmentData", None)
        super().save(*args, **kwargs)
        if attachmentData is not None and self.email.mailbox.save_attachments:
            self.save_to_storage(attachmentData)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`file_path` file on deletion.
        """
        super().delete(*args, **kwargs)

        if self.file_path:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.file_path)
                logger.debug(
                    "Successfully removed the attachment file from storage.",
                    exc_info=True,
                )
            except FileNotFoundError:
                logger.exception("%s was not found!", self.file_path)
            except OSError:
                logger.exception("An OS error occured removing %s!", self.file_path)
            except Exception:
                logger.exception(
                    "An unexpected error occured removing %s!", self.file_path
                )

    def save_to_storage(self, attachmentData: Message[str, str]) -> None:
        """Saves the attachment file to the storage.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.fileManagment.saveStore` to wrap the storing process.

        Args:
            attachmentData: The data of the attachment to be saved.
        """
        if self.file_path:
            logger.debug("%s is already stored.", self)
            return

        @saveStore
        def writeAttachment(
            file: BufferedWriter, attachmentData: Message[str, str]
        ) -> None:
            file.write(attachmentData.get_payload(decode=True))

        logger.debug("Storing %s ...", self)

        dirPath = StorageModel.getSubdirectory(self.email.message_id)
        preliminary_file_path = os.path.join(dirPath, self.file_name)

        if file_path := writeAttachment(preliminary_file_path, attachmentData):
            self.file_path = file_path
            self.save(update_fields=["file_path"])
            logger.debug("Successfully stored attachment.")
        else:
            logger.error("Failed to store %s!", self)

    @staticmethod
    def fromData(
        attachmentData: Message[str, str], email: EMailModel
    ) -> AttachmentModel:
        """Prepares a :class:`core.models.AttachmentModel.AttachmentModel` from attachment payload in bytes.

        Args:
            attachmentData: The attachment in bytes.
            email: The email the attachment was a part of.

        Returns:
            The :class:`core.models.AttachmentModel.AttachmentModel` instance with the file data.
        """
        new_attachment = AttachmentModel()
        new_attachment.file_name = (
            attachmentData.get_filename()
            or md5(attachmentData.as_bytes()).hexdigest()
            + f".{attachmentData.get_content_subtype()}"
        )
        new_attachment.content_disposition = (
            attachmentData.get_content_disposition() or ""
        )
        new_attachment.content_type = attachmentData.get_content_type()
        new_attachment.datasize = len(attachmentData.as_bytes())
        new_attachment.email = email

        return new_attachment

    @override
    @property
    def has_download(self):
        return self.file_path is not None

    @override
    @property
    def has_thumbnail(self):
        return self.content_type.startswith("image")

    @override
    def get_absolute_thumbnail_url(self) -> str:
        """Returns the url of the thumbail download api endpoint."""
        return reverse(f"api:v1:{self.BASENAME}-download", kwargs={"pk": self.pk})
