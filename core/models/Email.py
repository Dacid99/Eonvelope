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

from core.constants import HeaderFields
from core.mixins.FavoriteMixin import FavoriteMixin
from core.mixins.HasDownloadMixin import HasDownloadMixin
from core.mixins.HasThumbnailMixin import HasThumbnailMixin
from core.mixins.URLMixin import URLMixin
from core.models.EmailCorrespondent import EmailCorrespondent
from core.utils.fileManagment import clean_filename, saveStore
from core.utils.mailParsing import eml2html, is_X_Spam
from Emailkasten.utils.workarounds import get_config

from ..utils.mailParsing import get_bodytexts, getHeader, parseDatetimeHeader
from .Attachment import Attachment
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

    inReplyTo: models.ForeignKey[Email | None, Email | None] = models.ForeignKey(
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
    """The correspondents that are mentioned in this mail. Bridges through :class:`core.models.EmailCorrespondent.EmailCorrespondent`."""

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
        emailData = kwargs.pop("emailData", None)
        super().save(*args, **kwargs)
        if emailData is not None:
            if self.mailbox.save_toEML:
                self.save_eml_to_storage(emailData)
            if self.mailbox.save_toHTML:
                self.save_html_to_storage(emailData)

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

    def save_eml_to_storage(self, emailData: bytes) -> None:
        """Saves the email to the storage in eml format.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.fileManagment.saveStore` to wrap the storing process.

        Args:
            emailData: The data of the email to be saved.
        """
        if self.eml_filepath:
            logger.debug("%s is already stored as eml.", self)
            return

        @saveStore
        def writeMessageToEML(emlFile: BufferedWriter, emailData: bytes) -> None:
            emlFile.write(emailData)

        logger.debug("Storing %s as eml ...", self)

        dirPath = Storage.getSubdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dirPath, clean_message_id + ".eml")
        file_path = writeMessageToEML(preliminary_file_path, emailData)
        if file_path:
            self.eml_filepath = file_path
            self.save(update_fields=["eml_filepath"])
            logger.debug("Successfully stored email as eml.")
        else:
            logger.error("Failed to store %s as eml!", self)

    def save_html_to_storage(self, emailData: bytes) -> None:
        """Converts the email to html and writes the result to the storage.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.fileManagment.saveStore` to wrap the storing process.

        Args:
            emailData: The data of the email to be converted.
        """
        if self.html_filepath:
            logger.debug("%s is already stored as html.", self)
            return

        @saveStore
        def convertAndStoreHtmlMessage(
            htmlFile: BufferedWriter, emailData: bytes
        ) -> None:
            htmlMessage = eml2html(emailData)
            htmlFile.write(htmlMessage.encode())

        logger.debug("Rendering and storing %s  ...", self)

        dirPath = Storage.getSubdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dirPath, clean_message_id + ".html")
        file_path = convertAndStoreHtmlMessage(preliminary_file_path, emailData)
        if file_path:
            self.html_filepath = file_path
            self.save(update_fields=["html_filepath"])
            logger.debug("Successfully converted and stored email.")
        else:
            logger.error("Failed to convert and store %s!", self)

    def subConversation(self) -> list[Email]:
        """Gets all emails that are follow this email in the conversation.

        Returns:
            The list of all mails in the subconversation.
        """
        subConversationEmails = [self]
        for replyEmail in self.replies.all().prefetch_related("replies"):
            subConversationEmails.extend(replyEmail.subConversation())
        return subConversationEmails

    def fullConversation(self) -> list[Email]:
        """Gets all emails that are connected to this email via inReplyTo.

        Based on :func:`core.models.Email.Email.subConversation`
        to recurse through the entire conversation.

        Returns:
            The list of all mails in the conversation.
        """
        rootEmail = self
        while rootEmail.inReplyTo is not None:
            rootEmail = rootEmail.inReplyTo
        return rootEmail.subConversation()

    def isSpam(self) -> bool:
        """Checks the spam headers to decide whether the mail is spam.

        Returns:
            Whether the mail is considered spam.
        """
        return is_X_Spam(self.x_spam)

    @classmethod
    def fillFromEmailBytes(cls, email_bytes: bytes) -> Email:
        """Constructs an :class:`core.models.Email.Email` from an email in bytes form.

        Args:
            emailBytes: The email bytes to parse the emaildata from.

        Returns:
            The :class:`core.models.Email.Email` instance with data from the bytes.
        """
        email_message = email.message_from_bytes(email_bytes, policy=policy.default)  # type: ignore[arg-type]  # email stubs are not up-to-date for EmailMessage, will be fixed by mypy 1.16.0: https://github.com/python/typeshed/issues/13593
        headerDict = {}
        for headerName in email_message:
            headerDict[headerName] = getHeader(email_message, headerName)
        inReplyTo_message_id = headerDict.get(HeaderFields.IN_REPLY_TO)
        inReplyTo = None
        if inReplyTo_message_id:
            with contextlib.suppress(Email.DoesNotExist):
                inReplyTo = Email.objects.get(message_id=inReplyTo_message_id)
        bodytexts = get_bodytexts(email_message)
        return cls(
            headers=headerDict,
            message_id=headerDict.get(HeaderFields.MESSAGE_ID)
            or md5(email_bytes).hexdigest(),
            datetime=parseDatetimeHeader(headerDict.get(HeaderFields.DATE)),
            email_subject=headerDict.get(HeaderFields.SUBJECT) or __("No subject"),
            inReplyTo=inReplyTo,
            x_spam=headerDict.get(HeaderFields.X_SPAM) or "",
            datasize=len(email_bytes),
            plain_bodytext=bodytexts.get("plain", ""),
            html_bodytext=bodytexts.get("html", ""),
        )

    @classmethod
    def createFromEmailBytes(cls, emailBytes: bytes, mailbox: Mailbox) -> Email | None:
        """Creates an :class:`core.models.Email.Email` from an email in bytes form.

        Args:
            emailBytes: The email bytes to parse the emaildata from.
            mailbox: The mailbox the email is in.

        Returns:
            The :class:`core.models.Email.Email` instance with data from the bytes.
            None if there is no Message-ID header in :attr:`emailMessage`,
            if the mail already exists in the db or
            if the mail is spam and is supposed to be thrown out.
        """
        emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)  # type: ignore[arg-type]  # email stubs are not up-to-date for EmailMessage, will be fixed by mypy 1.16.0: https://github.com/python/typeshed/issues/13593

        message_id = (
            getHeader(
                emailMessage,
                HeaderFields.MESSAGE_ID,
            )
            or md5(emailBytes).hexdigest()  # noqa: S324  # no safe hash required here
        )
        x_spam = getHeader(emailMessage, HeaderFields.X_SPAM) or ""
        if is_X_Spam(x_spam) and get_config("THROW_OUT_SPAM"):
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

        new_email = cls.fillFromEmailBytes(email_bytes=emailBytes)
        new_email.mailbox = mailbox

        logger.debug("Successfully parsed email.")
        try:
            with transaction.atomic():
                new_email.mailinglist = MailingList.createFromEmailMessage(emailMessage)
                new_email.save(emailData=emailBytes)
                if new_email.headers:
                    for mention in HeaderFields.Correspondents.values:
                        correspondentHeader = new_email.headers.get(mention)
                        if correspondentHeader:
                            EmailCorrespondent.createFromHeader(
                                correspondentHeader, mention, new_email
                            )
                attachments = Attachment.createFromEmailMessage(emailMessage, new_email)
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
