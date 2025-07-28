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

import contextlib
import logging
import os
from functools import cached_property
from hashlib import md5
from io import BytesIO
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, override
from zipfile import ZipFile

from django.core.files.storage import default_storage
from django.db import models
from django.utils.text import get_valid_filename
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..constants import HeaderFields
from ..mixins import FavoriteMixin, HasDownloadMixin, HasThumbnailMixin, URLMixin


if TYPE_CHECKING:
    from email.message import EmailMessage
    from tempfile import _TemporaryFileWrapper

    from django.db.models import QuerySet

    from .Email import Email


logger = logging.getLogger(__name__)


class Attachment(
    HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model
):
    """Database model for an attachment file in a mail."""

    file_name = models.CharField(
        max_length=255,
        verbose_name=_("filename"),
    )
    """The filename of the attachment."""

    file_path = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("filepath"),
    )
    """The path in the storage where the attachment is stored. Unique together with :attr:`email`.
    Can be null if the attachment has not been saved (null does not collide with the unique constraint.).
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_Attachment.post_delete_attachment`."""

    content_disposition = models.CharField(
        blank=True,
        default="",
        max_length=255,
        verbose_name=_("content disposition"),
    )
    """The disposition of the file. Typically 'attachment', 'inline' or ''."""

    content_id = models.CharField(
        max_length=255,
        default="",
        verbose_name=_("content ID"),
    )
    """The MIME subtype of the file."""

    content_maintype = models.CharField(
        max_length=255,
        default="",
        verbose_name=_("content maintype"),
    )
    """The MIME maintype of the file."""

    content_subtype = models.CharField(
        max_length=255,
        default="",
        verbose_name=_("content subtype"),
    )
    """The MIME subtype of the file."""

    datasize = models.PositiveIntegerField(
        verbose_name=_("datasize"),
    )
    """The filesize of the attachment."""

    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_("favorite"),
    )
    """Flags favorite attachments. False by default."""

    email: models.ForeignKey[Email] = models.ForeignKey(
        "Email",
        related_name="attachments",
        on_delete=models.CASCADE,
        verbose_name=_("email"),
    )
    """The mail that the attachment was found in.  Deletion of that `email` deletes this attachment."""

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created"),
    )
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("last updated"),
    )
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "attachment"

    DELETE_NOTICE = _("This will only delete this attachment, not the email.")

    class Meta:
        """Metadata class for the model."""

        db_table = "attachments"
        """The name of the database table for the attachments."""

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

        Saves the data to storage if configured.
        """
        self.file_name = get_valid_filename(self.file_name)
        attachment_payload = kwargs.pop("attachment_payload", None)
        super().save(*args, **kwargs)
        if attachment_payload is not None and self.email.mailbox.save_attachments:
            self.save_to_storage(attachment_payload)

    def save_to_storage(self, attachment_payload: bytes) -> None:
        """Saves the attachment file to the storage.

        If the file already exists, does not overwrite.

        Args:
            attachment_payload: The data of the attachment to be saved.
        """
        if self.file_path:
            logger.debug("%s is already stored.", self)
            return

        logger.debug("Storing %s ...", self)

        self.file_path = default_storage.save(
            str(self.pk) + "_" + self.file_name,
            BytesIO(attachment_payload),
        )
        self.save(update_fields=["file_path"])
        logger.debug("Successfully stored attachment.")

    @staticmethod
    def queryset_as_file(queryset: QuerySet[Attachment]) -> _TemporaryFileWrapper:
        """Processes the files of the emails in the queryset into a temporary file.

        Args:
            queryset: The email queryset to compile into a file.

        Returns:
            The temporary file wrapper.

        Raises:
            Attachment.DoesNotExist: If the :attr:`queryset` is empty.
        """
        if not queryset.exists():
            raise Attachment.DoesNotExist("The queryset is empty!")
        tempfile = (
            NamedTemporaryFile()  # noqa: SIM115  # pylint: disable=consider-using-with
        )  #  the file must not be closed as it is returned later
        with ZipFile(tempfile.name, "w") as zipfile:
            for attachment_item in queryset:
                if attachment_item.file_path is not None:
                    with (
                        zipfile.open(
                            os.path.basename(attachment_item.file_path), "w"
                        ) as zipped_file,
                        contextlib.suppress(FileNotFoundError),
                    ):
                        zipped_file.write(
                            default_storage.open(attachment_item.file_path).read()
                        )
        return tempfile

    @classmethod
    def create_from_email_message(
        cls, email_message: EmailMessage, email: Email
    ) -> list[Attachment]:
        """Creates :class:`core.models.Attachment`s from an email message.

        Args:
            email_message: The email_message to get and create all attachments from.
            email: The email model created from the email_message.

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
    @cached_property
    def has_download(self) -> bool:
        return self.file_path is not None

    @override
    @cached_property
    def has_thumbnail(self) -> bool:
        """Whether the attachment has a mimetype that can be embedded into html.

        References:
            https://stackoverflow.com/questions/51107683/which-mime-types-can-be-displayed-in-browser
        """
        return self.file_path is not None and (
            self.content_maintype in ["image", "font"]
            or (
                self.content_maintype == "text"
                and not self.content_subtype.endswith("calendar")
            )
            or (
                self.content_maintype == "audio"
                and self.content_subtype in ["ogg", "wav", "mpeg", "aac"]
            )
            or (
                self.content_maintype == "video"
                and self.content_subtype in ["ogg", "mp4", "mpeg", "webm", "avi"]
            )
            or (
                self.content_maintype == "application"
                and (
                    self.content_subtype in ["pdf", "json"]
                    or self.content_subtype.endswith(("xml", "script"))
                )
            )
        )

    @override
    def get_absolute_thumbnail_url(self) -> str:
        """Returns the url of the thumbnail download api endpoint.

        As there is no dedicated thumbnail, it is identical to the download url.
        """
        return self.get_absolute_download_url()
