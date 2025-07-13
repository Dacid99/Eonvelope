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

"""Module with the :class:`Email` model class."""

from __future__ import annotations

import contextlib
import email
import logging
import os
import shutil
from email import policy
from functools import cached_property
from hashlib import md5
from io import BytesIO
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import TYPE_CHECKING, Any, Final, override
from zipfile import ZipFile

from django.core.files.storage import default_storage
from django.db import models, transaction
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..constants import HeaderFields, SupportedEmailDownloadFormats, file_format_parsers
from ..mixins import FavoriteMixin, HasDownloadMixin, HasThumbnailMixin, URLMixin
from ..utils.mail_parsing import (
    get_bodytexts,
    get_header,
    is_x_spam,
    message2html,
    parse_datetime_header,
)
from .Attachment import Attachment
from .EmailCorrespondent import EmailCorrespondent


if TYPE_CHECKING:
    from tempfile import _TemporaryFileWrapper

    from django.db.models import QuerySet

    from .Correspondent import Correspondent
    from .Mailbox import Mailbox


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Email(HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model):
    """Database model for an email."""

    message_id = models.CharField(
        max_length=255,
        verbose_name=_("message-ID"),
    )
    """The messageID header of the mail. Unique together with :attr:`mailbox`."""

    datetime = models.DateTimeField(
        verbose_name=_("received"),
    )
    """The Date header of the mail."""

    email_subject = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("subject"),
    )
    """The subject header of the mail."""

    plain_bodytext = models.TextField(
        blank=True,
        default="",
        verbose_name=_("plain bodytext"),
    )
    """The plain bodytext of the mail. Can be blank."""

    html_bodytext = models.TextField(
        blank=True,
        default="",
        verbose_name=_("HTML bodytext"),
    )
    """The html bodytext of the mail. Can be blank."""

    in_reply_to: models.ManyToManyField[Email, Email] = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="replies",
        verbose_name=_("in reply to"),
    )
    """The mails that this mail is a response to.
    Technically just a single mail, but as a mail can exist in multiple mailboxes, this needs to be able to reference multiples."""

    references: models.ManyToManyField[Email, Email] = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="referenced_by",
        verbose_name=_("referenced by"),
    )
    """The mails that this email references."""

    datasize = models.PositiveIntegerField(
        verbose_name=_("datasize"),
    )
    """The bytes size of the mail."""

    eml_filepath = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("EML filepath"),
    )
    """The path in the storage where the mail is stored in .eml format.
    Can be null if the mail has not been saved.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_Email.post_delete_email_files`.
    """

    html_version = models.TextField(
        default="",
        null=False,
        blank=True,
        verbose_name=_("HTML version"),
    )
    """A html version of the email."""

    is_favorite = models.BooleanField(
        default=False,
        verbose_name=_("favorite"),
    )
    """Flags favorite mails. False by default."""

    correspondents: models.ManyToManyField[Correspondent, Correspondent] = (
        models.ManyToManyField(
            "Correspondent",
            through="EmailCorrespondent",
            related_name="emails",
            verbose_name=_("correspondents"),
        )
    )
    """The correspondents that are mentioned in this mail. Bridges through :class:`core.models.EmailCorrespondent`."""

    mailbox: models.ForeignKey[Mailbox] = models.ForeignKey(
        "Mailbox",
        related_name="emails",
        on_delete=models.CASCADE,
        verbose_name=_("mailbox"),
    )
    """The mailbox that this mail has been found in. Unique together with :attr:`message_id`. Deletion of that `mailbox` deletes this mail."""

    headers = models.JSONField(
        null=True,
        verbose_name=_("headers"),
    )
    """All other header fields of the mail. Can be null."""

    x_spam = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("X-Spam"),
    )
    """The x_spam header of this mail. Can be blank."""

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

    BASENAME = "email"

    DELETE_NOTICE = _(
        "This will delete this email and all its attachments but not its correspondents."
    )

    class Meta:
        """Metadata class for the model."""

        db_table = "emails"
        """The name of the database table for the emails."""

        constraints: Final[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["message_id", "mailbox"],
                name="email_unique_together_message_id_mailbox",
            )
        ]
        """`message_id` and :attr:`mailbox` in combination are unique."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the email, using :attr:`message_id`, :attr:`datetime` and :attr:`mailbox`.
        """
        return _(
            "Email with ID %(message_id)s, received on %(datetime)s from %(mailbox)s"
        ) % {
            "message_id": self.message_id,
            "datetime": self.datetime,
            "mailbox": self.mailbox,
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method.

        Renders and saves the data to eml if configured.
        """
        email_data = kwargs.pop("email_data", None)
        super().save(*args, **kwargs)
        if email_data is not None and self.mailbox.save_to_eml:
            self.save_eml_to_storage(email_data)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`eml_filepath` files on deletion.
        """
        delete_return = super().delete(*args, **kwargs)

        if self.eml_filepath:
            logger.debug("Removing eml file for %s from storage ...", self)
            default_storage.delete(self.eml_filepath)
            logger.debug("Successfully removed the eml file from storage.")

        return delete_return

    def save_eml_to_storage(self, email_data: bytes) -> None:
        """Saves the email to the storage in eml format.

        If the file already exists, does not overwrite.

        Args:
            email_data: The data of the email to be saved.
        """
        if self.eml_filepath:
            logger.debug("%s is already stored as eml.", self)
            return

        logger.debug("Storing %s as eml ...", self)

        self.eml_filepath = default_storage.save(
            str(self.pk) + "_" + self.message_id + ".eml",
            BytesIO(email_data),
        )
        self.save(update_fields=["eml_filepath"])
        logger.debug("Successfully stored email as eml.")

    def sub_conversation(self) -> list[Email]:
        """Gets all emails that follow this email in the conversation.

        Returns:
            The list of all mails in the subconversation.
        """
        sub_conversation_emails = [self]
        for reply_email in self.replies.all().prefetch_related("replies"):
            sub_conversation_emails.extend(reply_email.sub_conversation())
        return sub_conversation_emails

    def full_conversation(self) -> list[Email]:
        """Gets all emails that are connected to this email via in_reply_to.

        Based on :func:`core.models.Email.Email.sub_conversation`
        to recurse through the entire conversation.

        Todo:
            This needs to be properly adapted to in_reply_to being many-to-many.

        Returns:
            The list of all mails in the conversation.
        """
        root_email = self
        while root_email.in_reply_to.first() is not None:
            root_email = root_email.in_reply_to.first()
        return root_email.sub_conversation()

    def is_spam(self) -> bool:
        """Checks the spam headers to decide whether the mail is spam.

        Returns:
            Whether the mail is considered spam.
        """
        return is_x_spam(self.x_spam)

    @staticmethod
    def queryset_as_file(
        queryset: QuerySet[Email], file_format: str
    ) -> _TemporaryFileWrapper:
        """Processes the files of the emails in the queryset into a temporary file.

        Args:
            queryset: The email queryset to compile into a file.
            file_format: The desired format of the file. Must be one of :class:`core.constants.SupportedEmailDownloadFormats`. Case-insensitive.

        Returns:
            The temporary file wrapper.

        Raises:
            ValueError: If the given :attr:`file_format` is not supported.
            Email.DoesNotExist: If the :attr:`queryset` is empty.
        """
        if not queryset.exists():
            raise Email.DoesNotExist("The queryset is empty!")
        tempfile = NamedTemporaryFile(
            suffix=".zip"
        )  # the suffix allows zipping to this file with shutil
        file_format = file_format.lower()
        if file_format == SupportedEmailDownloadFormats.ZIP_EML:
            with ZipFile(tempfile.name, "w") as zipfile:
                for email_item in queryset:
                    if email_item.eml_filepath is not None:
                        try:
                            eml_file = default_storage.open(email_item.eml_filepath)
                        except FileNotFoundError:
                            continue
                        else:
                            with zipfile.open(
                                os.path.basename(email_item.eml_filepath), "w"
                            ) as zipped_file:
                                zipped_file.write(eml_file.read())
        elif file_format in [
            SupportedEmailDownloadFormats.MBOX,
            SupportedEmailDownloadFormats.BABYL,
            SupportedEmailDownloadFormats.MMDF,
        ]:
            parser_class = file_format_parsers[file_format]
            parser = parser_class(tempfile.name, create=True)  # type: ignore[abstract]  # mailbox.Mailbox is used for typing only
            parser.lock()
            for email_item in queryset:
                if email_item.eml_filepath is not None:
                    with contextlib.suppress(FileNotFoundError):
                        parser.add(default_storage.open(email_item.eml_filepath))
            parser.close()
        elif file_format in [
            SupportedEmailDownloadFormats.MAILDIR,
            SupportedEmailDownloadFormats.MH,
        ]:
            with TemporaryDirectory() as tempdirpath:
                mailbox_path = os.path.join(tempdirpath, file_format)
                parser_class = file_format_parsers[file_format]
                parser = parser_class(mailbox_path, create=True)  # type: ignore[abstract]  # mailbox.Mailbox is used for typing only
                parser.lock()
                for email_item in queryset:
                    if email_item.eml_filepath is not None:
                        # this construction is necessary as Maildir.add can also raise FileNotFound
                        # if the directory is incorrectly structured, that warning must not be blocked
                        try:
                            eml_file = default_storage.open(email_item.eml_filepath)
                        except FileNotFoundError:
                            continue
                        parser.add(eml_file)
                parser.close()
                shutil.make_archive(
                    os.path.splitext(tempfile.name)[0], "zip", tempdirpath
                )
        else:
            raise ValueError("The given file format is not supported!")
        return tempfile

    @classmethod
    def fill_from_email_bytes(cls, email_bytes: bytes) -> Email:
        """Constructs an :class:`core.models.Email` from an email in bytes form.

        Args:
            email_bytes: The email bytes to parse the emaildata from.

        Returns:
            The :class:`core.models.Email` instance with data from the bytes.
        """
        email_message = email.message_from_bytes(email_bytes, policy=policy.default)
        header_dict: dict[str, str | None] = {}
        for header_name in email_message:
            header_dict[header_name.lower()] = get_header(email_message, header_name)
        bodytexts = get_bodytexts(email_message)
        return cls(
            headers=header_dict,
            message_id=header_dict.get(HeaderFields.MESSAGE_ID)
            or md5(email_bytes).hexdigest(),
            datetime=parse_datetime_header(header_dict.get(HeaderFields.DATE)),
            email_subject=header_dict.get(HeaderFields.SUBJECT) or __("No subject"),
            x_spam=header_dict.get(HeaderFields.X_SPAM, ""),
            datasize=len(email_bytes),
            plain_bodytext=bodytexts.get("plain", ""),
            html_bodytext=bodytexts.get("html", ""),
            html_version=message2html(email_message),
        )

    def add_correspondents(self) -> None:
        """Adds the correspondents from the headerfields to the model."""
        if self.headers:
            for mention in HeaderFields.Correspondents.values:
                correspondent_header = self.headers.get(mention)
                if correspondent_header:
                    new_emailcorrespondents = EmailCorrespondent.create_from_header(
                        correspondent_header, mention, self
                    )
                    if mention == HeaderFields.Correspondents.FROM:
                        for new_emailcorrespondent in new_emailcorrespondents:
                            new_emailcorrespondent.correspondent.list_id = (
                                self.headers.get(HeaderFields.MailingList.ID, "")
                            )
                            new_emailcorrespondent.correspondent.list_help = (
                                self.headers.get(HeaderFields.MailingList.HELP, "")
                            )
                            new_emailcorrespondent.correspondent.list_archive = (
                                self.headers.get(HeaderFields.MailingList.ARCHIVE, "")
                            )
                            new_emailcorrespondent.correspondent.list_subscribe = (
                                self.headers.get(HeaderFields.MailingList.SUBSCRIBE, "")
                            )
                            new_emailcorrespondent.correspondent.list_unsubscribe = (
                                self.headers.get(
                                    HeaderFields.MailingList.UNSUBSCRIBE, ""
                                )
                            )
                            new_emailcorrespondent.correspondent.list_unsubscribe_post = self.headers.get(
                                HeaderFields.MailingList.UNSUBSCRIBE_POST, ""
                            )
                            new_emailcorrespondent.correspondent.list_post = (
                                self.headers.get(HeaderFields.MailingList.POST, "")
                            )
                            new_emailcorrespondent.correspondent.list_owner = (
                                self.headers.get(HeaderFields.MailingList.OWNER, "")
                            )
                            new_emailcorrespondent.correspondent.save()

    def add_in_reply_to(self) -> None:
        """Adds the in-reply-to emails from the headerfields to the model."""
        if self.headers:
            in_reply_to_message_id = self.headers.get(HeaderFields.IN_REPLY_TO)
            if in_reply_to_message_id:
                for in_reply_to_email in Email.objects.filter(
                    message_id=in_reply_to_message_id.strip(),
                    mailbox__account__user=self.mailbox.account.user,
                ):
                    self.in_reply_to.add(in_reply_to_email)

    def add_references(self) -> None:
        """Adds the references from the headerfields to the model."""
        if self.headers:
            referenced_message_ids = self.headers.get(HeaderFields.REFERENCES)
            if referenced_message_ids:
                for referenced_message_id in referenced_message_ids.split(","):
                    for referenced_email in Email.objects.filter(
                        message_id=referenced_message_id.strip(),
                        mailbox__account__user=self.mailbox.account.user,
                    ):
                        self.references.add(referenced_email)

    @classmethod
    def create_from_email_bytes(
        cls, email_bytes: bytes, mailbox: Mailbox
    ) -> Email | None:
        """Creates an :class:`core.models.Email` from an email in bytes form.

        Args:
            email_bytes: The email bytes to parse the emaildata from.
            mailbox: The mailbox the email is in.

        Returns:
            The :class:`core.models.Email` instance with data from the bytes.
            None if there is no Message-ID header in :attr:`email_message`,
            if the mail already exists in the db or
            if the mail is spam and is supposed to be thrown out.
        """
        email_message = email.message_from_bytes(email_bytes, policy=policy.default)

        message_id = (
            get_header(
                email_message,
                HeaderFields.MESSAGE_ID,
            )
            or md5(email_bytes).hexdigest()  # noqa: S324  # no safe hash required here
        )
        x_spam = get_header(email_message, HeaderFields.X_SPAM) or ""
        if is_x_spam(x_spam) and get_config("THROW_OUT_SPAM"):
            logger.debug(
                "Skipping email with Message-ID %s in %s, it is flagged as spam.",
                message_id,
                mailbox,
            )
            return None

        if cls.objects.filter(message_id=message_id, mailbox=mailbox).exists():
            logger.debug(
                "Skipping email with Message-ID %s in %s, it already exists in the db.",
                message_id,
                mailbox,
            )
            return None

        new_email = cls.fill_from_email_bytes(email_bytes=email_bytes)
        new_email.mailbox = mailbox

        logger.debug("Successfully parsed email.")
        try:
            with transaction.atomic():
                new_email.save(email_data=email_bytes)
                new_email.add_correspondents()
                new_email.add_in_reply_to()
                new_email.add_references()
                attachments = Attachment.create_from_email_message(
                    email_message, new_email
                )
        except Exception:
            logger.exception(
                "Failed creating email from bytes: Error while saving email to db!"
            )
            return None
        return new_email

    @override
    @cached_property
    def has_download(self) -> bool:
        return self.eml_filepath is not None

    @override
    def get_absolute_thumbnail_url(self) -> str:
        """Email does not provide a url for thumbnail download."""
        return ""

    @override
    @cached_property
    def has_thumbnail(self) -> bool:
        return self.html_version != ""
