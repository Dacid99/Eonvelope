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

"""Module with the :class:`Attachment` model class."""

from __future__ import annotations

import logging
import os
from hashlib import md5
from typing import TYPE_CHECKING, Any, Final, override

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..constants import HeaderFields
from ..mixins import FavoriteMixin, HasDownloadMixin, HasThumbnailMixin, URLMixin
from ..utils.file_managment import clean_filename, save_store
from .Storage import Storage


if TYPE_CHECKING:
    from email.message import Message
    from io import BufferedWriter

    from .Email import Email


logger = logging.getLogger(__name__)


class Attachment(
    HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model
):
    """Database model for an attachment file in a mail."""

    file_name = models.CharField(max_length=255)
    """The filename of the attachment."""

    file_path = models.FilePathField(
        path=settings.STORAGE_PATH, max_length=511, recursive=True, null=True
    )
    """The path where the attachment is stored. Unique together with :attr:`email`.
    Can be null if the attachment has not been saved (null does not collide with the unique constraint.).
    Must contain :attr:`constance.get_config('STORAGE_PATH')`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_Attachment.post_delete_attachment`."""

    content_disposition = models.CharField(blank=True, default="", max_length=255)
    """The disposition of the file. Typically 'attachment', 'inline' or ''."""

    content_id = models.CharField(max_length=255, default="")
    """The MIME subtype of the file."""

    content_maintype = models.CharField(max_length=255, default="")
    """The MIME maintype of the file."""

    content_subtype = models.CharField(max_length=255, default="")
    """The MIME subtype of the file."""

    datasize = models.PositiveIntegerField()
    """The filesize of the attachment."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite attachments. False by default."""

    email: models.ForeignKey[Email] = models.ForeignKey(
        "Email", related_name="attachments", on_delete=models.CASCADE
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

    @override
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
        attachment_payload = kwargs.pop("attachment_payload", None)
        super().save(*args, **kwargs)
        if attachment_payload is not None and self.email.mailbox.save_attachments:
            self.save_to_storage(attachment_payload)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`file_path` file on deletion.
        """
        delete_return = super().delete(*args, **kwargs)

        if self.file_path:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.file_path)
                logger.debug(
                    "Successfully removed the attachment file from storage.",
                    exc_info=True,
                )
            except Exception:
                logger.exception("An exception occured removing %s!", self.file_path)

        return delete_return

    def save_to_storage(self, attachment_payload: bytes) -> None:
        """Saves the attachment file to the storage.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.file_managment.save_store` to wrap the storing process.

        Args:
            attachment_data: The data of the attachment to be saved.
        """
        if self.file_path:
            logger.debug("%s is already stored.", self)
            return

        @save_store
        def write_attachment(file: BufferedWriter, attachment_payload: bytes) -> None:
            file.write(attachment_payload)

        logger.debug("Storing %s ...", self)

        dir_path = Storage.get_subdirectory(self.email.message_id)
        preliminary_file_path = os.path.join(dir_path, self.file_name)
        file_path = write_attachment(preliminary_file_path, attachment_payload)
        if file_path:
            self.file_path = file_path
            self.save(update_fields=["file_path"])
            logger.debug("Successfully stored attachment.")
        else:
            logger.error("Failed to store %s!", self)

    @classmethod
    def create_from_email_message(
        cls, email_message: Message[str, str], email: Email
    ) -> list[Attachment]:
        """Creates :class:`core.models.Attachment`s from an email message.

        Args:
            email_message: The email_message to get and create all attachments from.

        Returns:
            A list of :class:`core.models.Attachment` in the email message.
        """
        if email.pk is None:
            raise ValueError("Email is not in db!")
        save_maintypes = get_config("SAVE_CONTENT_TYPE_PREFIXES")
        ignore_subtypes = get_config("DONT_SAVE_CONTENT_TYPE_SUFFIXES")
        new_attachments = []
        for part in email_message.walk():
            if part.is_multipart():
                # for safe get_payload
                continue
            content_disposition = part.get_content_disposition()
            content_maintype = part.get_content_maintype()
            content_subtype = part.get_content_subtype()
            if content_disposition or (
                content_maintype in save_maintypes
                and content_subtype not in ignore_subtypes
            ):
                part_payload = part.get_payload(decode=True)
                if isinstance(part_payload, bytes):
                    new_attachment = cls(
                        file_name=(
                            part.get_filename()
                            or md5(  # noqa: S324  # no safe hash required here
                                part_payload
                            ).hexdigest()
                            + f".{content_subtype}"
                        ),
                        content_disposition=content_disposition or "",
                        content_id=part.get(HeaderFields.CONTENT_ID, ""),
                        content_maintype=content_maintype,
                        content_subtype=content_subtype,
                        datasize=len(part_payload),
                        email=email,
                    )
                    new_attachment.save(attachment_payload=part_payload)
                    new_attachments.append(new_attachment)
        return new_attachments

    @override
    @property
    def has_download(self) -> bool:
        return self.file_path is not None

    @override
    @property
    def has_thumbnail(self) -> bool:
        return self.content_maintype == "image"

    @override
    def get_absolute_thumbnail_url(self) -> str:
        """Returns the url of the thumbail download api endpoint."""
        return reverse(f"api:v1:{self.BASENAME}-download", kwargs={"pk": self.pk})
