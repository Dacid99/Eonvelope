# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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
from functools import cached_property
from hashlib import md5
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Any, override
from zipfile import ZipFile

import httpcore
import httpx
from django.db import models
from django.utils.html import format_html
from django.utils.text import get_valid_filename
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin
from rest_framework import status

from core.constants import (
    HTML_SUPPORTED_AUDIO_TYPE,
    HTML_SUPPORTED_VIDEO_TYPES,
    IMMICH_SUPPORTED_APPLICATION_TYPES,
    IMMICH_SUPPORTED_IMAGE_TYPES,
    IMMICH_SUPPORTED_VIDEO_TYPES,
    PAPERLESS_SUPPORTED_IMAGE_TYPES,
    PAPERLESS_TIKA_SUPPORTED_MIMETYPES,
    HeaderFields,
)
from core.mixins import (
    DownloadMixin,
    FavoriteModelMixin,
    FilePathModelMixin,
    ThumbnailMixin,
    TimestampModelMixin,
    URLMixin,
)
from eonvelope.utils.workarounds import get_config


if TYPE_CHECKING:
    from email.message import EmailMessage
    from tempfile import _TemporaryFileWrapper

    from django.db.models import QuerySet

    from .Email import Email


logger = logging.getLogger(__name__)


class Attachment(
    ExportModelOperationsMixin("attachment"),
    DownloadMixin,
    ThumbnailMixin,
    URLMixin,
    FavoriteModelMixin,
    FilePathModelMixin,
    TimestampModelMixin,
    models.Model,
):
    """Database model for an attachment file in a mail."""

    BASENAME = "attachment"

    DELETE_NOTICE = _(
        "This will only delete the record of this attachment, not of the email."
    )

    DELETE_NOTICE_PLURAL = _(
        "This will only delete the records of these attachments, not of their emails."
    )

    file_name = models.CharField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("filename"),
    )
    """The filename of the attachment."""

    content_disposition = models.CharField(
        blank=True,
        default="",
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("content disposition"),
    )
    """The disposition of the file. Typically 'attachment', 'inline' or ''."""

    content_id = models.CharField(
        max_length=255,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("content ID"),
    )
    """The MIME subtype of the file."""

    content_maintype = models.CharField(
        max_length=255,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("content maintype"),
    )
    """The MIME maintype of the file."""

    content_subtype = models.CharField(
        max_length=255,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("content subtype"),
    )
    """The MIME subtype of the file."""

    datasize = models.PositiveIntegerField(
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("datasize"),
    )
    """The filesize of the attachment."""

    email: models.ForeignKey[Email] = models.ForeignKey(
        "Email",
        related_name="attachments",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("email"),
    )
    """The mail that the attachment was found in.  Deletion of that `email` deletes this attachment."""

    class Meta:
        """Metadata class for the model."""

        db_table = "attachments"
        """The name of the database table for the attachments."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("attachment")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("attachments")
        get_latest_by = "email__datetime"

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
        if not self.email.mailbox.save_attachments:
            kwargs.pop("file_payload", None)
        super().save(*args, **kwargs)

    @override
    def _get_storage_file_name(self) -> str:
        """Create the filename for the stored attachment."""
        return str(self.pk) + "_" + self.file_name

    def share_to_paperless(self) -> str:
        """Sends this attachment to the Paperless server of its user.

        Returns:
            The uuid string of the Paperless consumer task for the document.

        Raises:
            FileNotFoundError: If the attachment file was not found in the storage.
            RuntimeError: If the users Paperless URL is not or improperly set.
            ConnectionError: If connecting to Paperless failed.
            PermissionError: If authentication to Paperless failed.
            ValueError: If uploading the file to Paperless resulted in a bad response.
        """
        paperless_baseurl = (
            self.email.mailbox.account.user.profile.paperless_url.rstrip("/")
        )
        logger.debug(
            "Sending %s to Paperless server at %s ...", str(self), paperless_baseurl
        )
        post_document_url = paperless_baseurl + "/api/documents/post_document/"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Token {self.email.mailbox.account.user.profile.paperless_api_key}".strip(),
        }  # stripping the entire string to create a valid header even if the token is empty
        try:
            with self.open_file() as document:
                response = httpx.post(
                    post_document_url,
                    headers=headers,
                    data={"title": self.file_name, "created": str(self.created)},
                    files={"document": (self.file_name, document, self.content_type)},
                )
        except (
            httpcore.UnsupportedProtocol,
            httpx.UnsupportedProtocol,
            httpx.InvalidURL,
        ) as error:
            logger.info(
                "Failed to send attachment to Paperless.",
                exc_info=True,
            )
            raise RuntimeError(
                # Translators: Paperless is a brand name.
                _("Paperless URL is malformed: %(error)s")
                % {"error": error}
            ) from error
        except httpx.RequestError as error:
            logger.info("Failed to send attachment to Paperless.", exc_info=True)
            raise ConnectionError(
                # Translators: Paperless is a brand name.
                _("Error connecting to the Paperless server: %(error)s")
                % {"error": error}
            ) from error
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            logger.info("Failed to send attachment to Paperless.", exc_info=True)
            if error.response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]:
                raise PermissionError(
                    # Translators: Paperless is a brand name.
                    _("Authentication to Paperless failed: %(response)s")
                    % {"response": error.response.json()}
                ) from error
            raise ValueError(
                # Translators: Paperless is a brand name.
                _("Uploading to Paperless failed: %(response)s")
                % {"response": error.response.json()}
            ) from error
        logger.debug("Successfully sent attachment to Paperless.")
        return response.json()

    def share_to_immich(self) -> str:
        """Sends this attachment to the Immich server of its user.

        Returns:
            The response by Immich with the id string of the stored immich image.

        Raises:
            FileNotFoundError: If the attachment file was not found in the storage.
            RuntimeError: If the users Immich URL is not or improperly set.
            ConnectionError: If connecting to Immich failed.
            PermissionError: If authentication to Immich failed.
            ValueError: If uploading the file to Immich resulted in a bad response.
        """
        immich_baseurl = self.email.mailbox.account.user.profile.immich_url.rstrip("/")
        logger.debug("Sending %s to Immich server at %s ...", str(self), immich_baseurl)
        post_document_url = immich_baseurl + "/api/assets"
        headers = {
            "Accept": "application/json",
            "x-api-key": self.email.mailbox.account.user.profile.immich_api_key.strip(),
        }
        try:
            with self.open_file() as image_file:
                response = httpx.post(
                    post_document_url,
                    headers=headers,
                    data={
                        "assetId": self.file_name,
                        "deviceAssetId": "eonvelope",
                        "deviceId": "eonvelope",
                        "fileCreatedAt": str(self.created.date()),
                        "fileModifiedAt": str(self.created.date()),
                        "metadata": [],
                    },
                    files={
                        "assetData": (self.file_name, image_file, self.content_type)
                    },
                )
        except (
            httpcore.UnsupportedProtocol,
            httpx.UnsupportedProtocol,
            httpx.InvalidURL,
        ) as error:
            logger.info(
                "Failed to send attachment to Immich.",
                exc_info=True,
            )
            raise RuntimeError(
                # Translators: Immich is a brand name.
                _("Immich URL is malformed: %(error)s")
                % {"error": error}
            ) from error
        except httpx.RequestError as error:
            logger.info("Failed to send attachment to Immich.", exc_info=True)
            raise ConnectionError(
                # Translators: Immich is a brand name.
                _("Error connecting to the Immich server: %(error)s")
                % {"error": error}
            ) from error
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            logger.info("Failed to send attachment to Immich.", exc_info=True)
            if error.response.status_code in [
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            ]:
                raise PermissionError(
                    # Translators: Immich is a brand name.
                    _("Authentication to Immich failed: %(response)s")
                    % {"response": error.response.json()}
                ) from error
            raise ValueError(
                # Translators: Immich is a brand name.
                _("Uploading to Immich failed: %(response)s")
                % {"response": error.response.json()}
            ) from error
        logger.debug("Successfully sent attachment to Immich.")
        return response.json()

    @override
    @cached_property
    def has_thumbnail(self) -> bool:
        """Whether the attachment has a mimetype that can be embedded into html.

        References:
            https://stackoverflow.com/questions/51107683/which-mime-types-can-be-displayed-in-browser
        """
        return (
            super().has_thumbnail
            and not self.email.is_spam
            and (self.datasize <= get_config("WEB_THUMBNAIL_MAX_DATASIZE"))
            and (
                self.content_maintype in ["image", "font"]
                or (
                    self.content_maintype == "text"
                    and not self.content_subtype.endswith("calendar")
                )
                or (
                    self.content_maintype == "audio"
                    and self.content_subtype in HTML_SUPPORTED_AUDIO_TYPE
                )
                or (
                    self.content_maintype == "video"
                    and self.content_subtype in HTML_SUPPORTED_VIDEO_TYPES
                )
                or (
                    self.content_maintype == "application"
                    and (
                        self.content_subtype in ["pdf", "json"]
                        or self.content_subtype.endswith(("xml", "script"))
                    )
                )
            )
        )

    @cached_property
    def thumbnail(self) -> str:
        """Builds the html thumbnail for the attachment.

        Returns:
            The html for the thumbnail. The empty string if the attachment has no thumbnail.
        """
        if self.content_maintype == "audio":
            return format_html(
                """<div class="d-flex justify-content-center m-5">
                <audio controls src="{src}"></audio>
                          </div>
                          """,
                src=self.get_absolute_thumbnail_url(),
            )
        if self.content_maintype == "video":
            return format_html(
                """<video controls
                preload="metadata"
                class="img-thumbnail"
                src="{src}">
            </video>
            """,
                src=self.get_absolute_thumbnail_url(),
            )
        if self.content_maintype == "image":
            return format_html(
                """<img src="{src}"
                class="img-thumbnail"
                alt="{alt}" />
                """,
                src=self.get_absolute_thumbnail_url(),
                alt=_("Attachment image"),
            )
        if self.content_maintype == "text":
            return format_html(
                """<iframe sandbox
                    class="w-100 h-100 p-1 rounded"
                    title="{alt}"
                    src="{src}"></iframe>
                    """,
                src=self.get_absolute_thumbnail_url(),
                alt=_("Attachment text"),
            )
        if self.content_maintype == "application":
            return format_html(
                """<embed class="w-100 h-100 p-1 rounded"
                title={title}"
                src="{src}" />
                """,
                src=self.get_absolute_thumbnail_url(),
                title=_("Attachment file content"),
            )
        if self.content_maintype == "font":
            return format_html(
                """<style>
                @font-face {{
                    font-family: attachment_{id};
                    src: url({src});
                }}
            </style>
            <h1 class="text-center p-2"
                style="font-family: attachment_{id}">
                Aa
                <br />
                Zz
                <br />
                12
            </h1>
            """,
                src=self.get_absolute_thumbnail_url(),
                id=self.id,
            )
        return ""

    @property
    def content_type(self) -> str:
        """Reconstructs the full MIME content type of the attachment.

        Returns:
            The attachments content type if known, else "".
        """
        if self.content_maintype and self.content_subtype:
            return self.content_maintype + "/" + self.content_subtype
        return ""

    @property
    def is_shareable_to_paperless(self) -> bool:
        """Whether the attachment has a mimetype that can be processed by a paperless server.

        References:
            https://docs.paperless-ngx.com/faq/#what-file-types-does-paperless-ngx-support
        """
        return self.file_path is not None and (
            (self.content_maintype == "text" and self.content_subtype == "plain")
            or (
                self.content_maintype == "image"
                and self.content_subtype in PAPERLESS_SUPPORTED_IMAGE_TYPES
            )
            or (
                self.content_maintype == "application"
                and (
                    self.content_subtype == "pdf"
                    or (
                        self.email.mailbox.account.user.profile.paperless_tika_enabled
                        and self.content_subtype in PAPERLESS_TIKA_SUPPORTED_MIMETYPES
                    )
                )
            )
        )

    @property
    def is_shareable_to_immich(self) -> bool:
        """Whether the attachment has a mimetype that can be processed by a Immich server.

        References:
            https://immich.app/docs/features/supported-formats/
        """
        return self.file_path is not None and (
            (
                self.content_maintype == "image"
                and self.content_subtype in IMMICH_SUPPORTED_IMAGE_TYPES
            )
            or (
                self.content_maintype == "video"
                and self.content_subtype in IMMICH_SUPPORTED_VIDEO_TYPES
            )
            or (
                self.content_maintype == "application"
                and self.content_subtype in IMMICH_SUPPORTED_APPLICATION_TYPES
            )
        )

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
        logger.debug("Parsing and saving attachments in email %s ...", email.message_id)
        ignore_maintypes = get_config("DONT_PARSE_CONTENT_MAINTYPES")
        ignore_subtypes = get_config("DONT_PARSE_CONTENT_SUBTYPES")
        new_attachments = []
        for part in email_message.walk():
            if part.is_multipart():
                # for safe get_payload
                continue
            content_disposition = part.get_content_disposition()
            content_maintype = part.get_content_maintype()
            content_subtype = part.get_content_subtype()
            # first part of the condition checks whether the part qualifies as attachment in general,
            # the second one whether the parts contenttype is blacklisted
            if (
                content_disposition
                or (
                    content_maintype != "text"
                    or content_subtype not in ["plain", "html"]
                )
            ) and (
                content_maintype not in ignore_maintypes
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
                    logger.debug("Saving attachment %s to db ...", part.get_filename())
                    new_attachment.save(file_payload=part_payload)
                    new_attachments.append(new_attachment)
        logger.debug("Successfully parsed and saved attachments.")
        return new_attachments

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
                try:
                    attachment_file = attachment_item.open_file()
                except FileNotFoundError:
                    continue
                with (
                    attachment_file,
                    zipfile.open(
                        os.path.basename(attachment_item.file_path), "w"
                    ) as zipped_file,
                ):
                    zipped_file.write(attachment_file.read())
        return tempfile
