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
from email import policy
from hashlib import md5
from typing import TYPE_CHECKING, Any, Final, override

from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext as __
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..constants import HeaderFields
from ..mixins import FavoriteMixin, HasDownloadMixin, HasThumbnailMixin, URLMixin
from ..utils.file_managment import clean_filename, save_store
from ..utils.mail_parsing import (
    eml2html,
    get_bodytexts,
    get_header,
    is_x_spam,
    parse_datetime_header,
)
from .Attachment import Attachment
from .EmailCorrespondent import EmailCorrespondent
from .MailingList import MailingList
from .Storage import Storage


if TYPE_CHECKING:
    from io import BufferedWriter

    from .Correspondent import Correspondent
    from .Mailbox import Mailbox


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Email(HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model):
    """Database model for an email."""

    message_id = models.CharField(max_length=255)
    """The messageID header of the mail. Unique together with :attr:`mailbox`."""

    datetime = models.DateTimeField()
    """The Date header of the mail."""

    email_subject = models.CharField(max_length=255, blank=True, default="")
    """The subject header of the mail."""

    plain_bodytext = models.TextField(blank=True, default="")
    """The plain bodytext of the mail. Can be blank."""

    html_bodytext = models.TextField(blank=True, default="")
    """The html bodytext of the mail. Can be blank."""

    in_reply_to: models.ForeignKey[Email | None, Email | None] = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.SET_NULL
    )
    """The mail that this mail is a response to. Can be null. Deletion of that replied-to mail sets this field to NULL."""

    datasize = models.PositiveIntegerField()
    """The bytes size of the mail."""

    eml_filepath = models.FilePathField(
        path=settings.STORAGE_PATH,
        max_length=255,
        recursive=True,
        match=r".*\.eml$",
        null=True,
    )
    """The path where the mail is stored in .eml format.
    Can be null if the mail has not been saved.
    Must contain :attr:`constance.get_config('STORAGE_PATH')` and end on .eml .
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_Email.post_delete_email_files`.
    """

    html_filepath = models.FilePathField(
        path=settings.STORAGE_PATH,
        max_length=255,
        recursive=True,
        match=r".*\.html$",
        null=True,
    )
    """The path where the html version of the mail is stored.
    Can be null if the conversion process was no successful.
    Must contain :attr:`constance.get_config('STORAGE_PATH')` and end on `.html`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_Email.post_delete_email_files`."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mails. False by default."""

    correspondents: models.ManyToManyField[Correspondent, Correspondent] = (
        models.ManyToManyField(
            "Correspondent",
            through="EmailCorrespondent",
            related_name="emails",
        )
    )
    """The correspondents that are mentioned in this mail. Bridges through :class:`core.models.EmailCorrespondent`."""

    mailinglist: models.ForeignKey[MailingList | None, MailingList | None] = (
        models.ForeignKey(
            "MailingList",
            null=True,
            related_name="emails",
            on_delete=models.CASCADE,
        )
    )
    """The mailinglist that this mail has been sent from. Can be null. Deletion of that `mailinglist` deletes this mail."""

    mailbox: models.ForeignKey[Mailbox] = models.ForeignKey(
        "Mailbox", related_name="emails", on_delete=models.CASCADE
    )
    """The mailbox that this mail has been found in. Unique together with :attr:`message_id`. Deletion of that `mailbox` deletes this mail."""

    headers = models.JSONField(null=True)
    """All other header fields of the mail. Can be null."""

    x_spam = models.CharField(max_length=255, blank=True, default="")
    """The x_spam header of this mail. Can be blank."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "email"

    DELETE_NOTICE = _(
        "This will delete this email and all its attachments but not its correspondents or mailinglists."
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

        Renders and save the data to eml if configured.
        """
        email_data = kwargs.pop("email_data", None)
        super().save(*args, **kwargs)
        if email_data is not None:
            if self.mailbox.save_to_eml:
                self.save_eml_to_storage(email_data)
            if self.mailbox.save_to_html:
                self.save_html_to_storage(email_data)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`eml_filepath` and :attr:`html_filepath` files on deletion.
        """
        delete_return = super().delete(*args, **kwargs)

        if self.eml_filepath:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.eml_filepath)
                logger.debug(
                    "Successfully removed the eml file from storage.", exc_info=True
                )
            except Exception:
                logger.exception("An exception occured removing %s!", self.eml_filepath)

        if self.html_filepath:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.html_filepath)
                logger.debug(
                    "Successfully removed the html file from storage.",
                    exc_info=True,
                )
            except Exception:
                logger.exception(
                    "An exception occured removing %s!", self.html_filepath
                )

        return delete_return

    def save_eml_to_storage(self, email_data: bytes) -> None:
        """Saves the email to the storage in eml format.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.file_managment.save_store` to wrap the storing process.

        Args:
            email_data: The data of the email to be saved.
        """
        if self.eml_filepath:
            logger.debug("%s is already stored as eml.", self)
            return

        @save_store
        def write_message_to_eml(eml_file: BufferedWriter, email_data: bytes) -> None:
            eml_file.write(email_data)

        logger.debug("Storing %s as eml ...", self)

        dir_path = Storage.get_subdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dir_path, clean_message_id + ".eml")
        file_path = write_message_to_eml(preliminary_file_path, email_data)
        if file_path:
            self.eml_filepath = file_path
            self.save(update_fields=["eml_filepath"])
            logger.debug("Successfully stored email as eml.")
        else:
            logger.error("Failed to store %s as eml!", self)

    def save_html_to_storage(self, email_data: bytes) -> None:
        """Converts the email to html and writes the result to the storage.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.file_managment.save_store` to wrap the storing process.

        Args:
            email_data: The data of the email to be converted.
        """
        if self.html_filepath:
            logger.debug("%s is already stored as html.", self)
            return

        @save_store
        def convert_and_store_html_message(
            html_file: BufferedWriter, email_data: bytes
        ) -> None:
            html_message = eml2html(email_data)
            html_file.write(html_message.encode())

        logger.debug("Rendering and storing %s  ...", self)

        dir_path = Storage.get_subdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dir_path, clean_message_id + ".html")
        file_path = convert_and_store_html_message(preliminary_file_path, email_data)
        if file_path:
            self.html_filepath = file_path
            self.save(update_fields=["html_filepath"])
            logger.debug("Successfully converted and stored email.")
        else:
            logger.error("Failed to convert and store %s!", self)

    def sub_conversation(self) -> list[Email]:
        """Gets all emails that are follow this email in the conversation.

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

        Returns:
            The list of all mails in the conversation.
        """
        root_email = self
        while root_email.in_reply_to is not None:
            root_email = root_email.in_reply_to
        return root_email.sub_conversation()

    def is_spam(self) -> bool:
        """Checks the spam headers to decide whether the mail is spam.

        Returns:
            Whether the mail is considered spam.
        """
        return is_x_spam(self.x_spam)

    @classmethod
    def fill_from_email_bytes(cls, email_bytes: bytes) -> Email:
        """Constructs an :class:`core.models.Email` from an email in bytes form.

        Args:
            email_bytes: The email bytes to parse the emaildata from.

        Returns:
            The :class:`core.models.Email` instance with data from the bytes.
        """
        email_message = email.message_from_bytes(email_bytes, policy=policy.default)  # type: ignore[arg-type]  # email stubs are not up-to-date for EmailMessage, will be fixed by mypy 1.16.0: https://github.com/python/typeshed/issues/13593
        header_dict = {}
        for header_name in email_message:
            header_dict[header_name] = get_header(email_message, header_name)
        in_reply_to_message_id = header_dict.get(HeaderFields.IN_REPLY_TO)
        in_reply_to = None
        if in_reply_to_message_id:
            with contextlib.suppress(Email.DoesNotExist):
                in_reply_to = Email.objects.get(message_id=in_reply_to_message_id)
        bodytexts = get_bodytexts(email_message)
        return cls(
            headers=header_dict,
            message_id=header_dict.get(HeaderFields.MESSAGE_ID)
            or md5(email_bytes).hexdigest(),
            datetime=parse_datetime_header(header_dict.get(HeaderFields.DATE)),
            email_subject=header_dict.get(HeaderFields.SUBJECT) or __("No subject"),
            in_reply_to=in_reply_to,
            x_spam=header_dict.get(HeaderFields.X_SPAM) or "",
            datasize=len(email_bytes),
            plain_bodytext=bodytexts.get("plain", ""),
            html_bodytext=bodytexts.get("html", ""),
        )

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
        email_message = email.message_from_bytes(email_bytes, policy=policy.default)  # type: ignore[arg-type]  # email stubs are not up-to-date for EmailMessage, will be fixed by mypy 1.16.0: https://github.com/python/typeshed/issues/13593

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
                new_email.mailinglist = MailingList.create_from_email_message(
                    email_message
                )
                new_email.save(email_data=email_bytes)
                if new_email.headers:
                    for mention in HeaderFields.Correspondents.values:
                        correspondent_header = new_email.headers.get(mention)
                        if correspondent_header:
                            EmailCorrespondent.create_from_header(
                                correspondent_header, mention, new_email
                            )
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
    @property
    def has_download(self) -> bool:
        return self.eml_filepath is not None

    @override
    @property
    def has_thumbnail(self) -> bool:
        return self.html_filepath is not None
