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

"""Module with the :class:`EMailModel` model class."""

from __future__ import annotations

import email
import logging
import os
from email import policy
from hashlib import md5
from typing import TYPE_CHECKING, Any, Final, override

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from core.constants import HeaderFields
from core.mixins.FavoriteMixin import FavoriteMixin
from core.mixins.HasDownloadMixin import HasDownloadMixin
from core.mixins.HasThumbnailMixin import HasThumbnailMixin
from core.mixins.URLMixin import URLMixin
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.utils.fileManagment import clean_filename, saveStore
from core.utils.mailParsing import eml2html, is_X_Spam
from Emailkasten.utils import get_config

from ..utils.mailParsing import getHeader, parseDatetimeHeader
from .AttachmentModel import AttachmentModel
from .MailingListModel import MailingListModel
from .StorageModel import StorageModel


if TYPE_CHECKING:
    from io import BufferedWriter

    from .CorrespondentModel import CorrespondentModel
    from .MailboxModel import MailboxModel


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class EMailModel(
    HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model
):
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

    inReplyTo: models.ForeignKey[EMailModel] = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.SET_NULL
    )
    """The mail that this mail is a response to. Can be null. Deletion of that replied-to mail sets this field to NULL."""

    datasize = models.PositiveIntegerField()
    """The bytes size of the mail."""

    eml_filepath = models.FilePathField(
        path=get_config("STORAGE_PATH"),
        max_length=255,
        recursive=True,
        match=r".*\.eml$",
        null=True,
    )
    """The path where the mail is stored in .eml format.
    Can be null if the mail has not been saved.
    Must contain :attr:`constance.get_config('STORAGE_PATH')` and end on .eml .
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_EMailModel.post_delete_email_files`.
    """

    html_filepath = models.FilePathField(
        path=get_config("STORAGE_PATH"),
        max_length=255,
        recursive=True,
        match=r".*\.html$",
        null=True,
    )
    """The path where the html version of the mail is stored.
    Can be null if the conversion process was no successful.
    Must contain :attr:`constance.get_config('STORAGE_PATH')` and end on `.html`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_EMailModel.post_delete_email_files`."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mails. False by default."""

    correspondents: models.ManyToManyField[CorrespondentModel] = models.ManyToManyField(
        "CorrespondentModel", through="EMailCorrespondentsModel", related_name="emails"
    )
    """The correspondents that are mentioned in this mail. Bridges through :class:`core.models.EMailCorrespondentsModel`."""

    mailinglist: models.ForeignKey[MailingListModel] = models.ForeignKey(
        "MailingListModel", null=True, related_name="emails", on_delete=models.CASCADE
    )
    """The mailinglist that this mail has been sent from. Can be null. Deletion of that `mailinglist` deletes this mail."""

    mailbox: models.ForeignKey[MailboxModel] = models.ForeignKey(
        "MailboxModel", related_name="emails", on_delete=models.CASCADE
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
    def delete(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`eml_filepath` and :attr:`html_filepath` files on deletion.
        """
        super().delete(*args, **kwargs)

        if self.eml_filepath:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.eml_filepath)
                logger.debug(
                    "Successfully removed the eml file from storage.", exc_info=True
                )
            except FileNotFoundError:
                logger.exception("%s was not found!", self.eml_filepath)
            except OSError:
                logger.exception("An OS error occured removing %s!", self.eml_filepath)
            except Exception:
                logger.exception(
                    "An unexpected error occured removing %s!", self.eml_filepath
                )

        if self.html_filepath:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.html_filepath)
                logger.debug(
                    "Successfully removed the html file from storage.",
                    exc_info=True,
                )
            except FileNotFoundError:
                logger.exception("%s was not found!", self.html_filepath)
            except OSError:
                logger.exception("An OS error occured removing %s!", self.html_filepath)
            except Exception:
                logger.exception(
                    "An unexpected error occured removing %s!", self.html_filepath
                )

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

        dirPath = StorageModel.getSubdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dirPath, clean_message_id + ".eml")
        if file_path := writeMessageToEML(preliminary_file_path, emailData):
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

        dirPath = StorageModel.getSubdirectory(self.message_id)
        clean_message_id = clean_filename(self.message_id)
        preliminary_file_path = os.path.join(dirPath, clean_message_id + ".html")
        if file_path := convertAndStoreHtmlMessage(preliminary_file_path, emailData):
            self.html_filepath = file_path
            self.save(update_fields=["html_filepath"])
            logger.debug("Successfully converted and stored email.")
        else:
            logger.error("Failed to convert and store %s!", self)

    def subConversation(self) -> list[EMailModel]:
        """Gets all emails that are follow this email in the conversation.

        Returns:
            The list of all mails in the subconversation.
        """
        subConversationEmails = [self]
        for replyEmail in self.replies.all():
            subConversationEmails.extend(replyEmail.subConversation())
        return subConversationEmails

    def fullConversation(self) -> list[EMailModel]:
        """Gets all emails that are connected to this email via inReplyTo.

        Based on :func:`core.models.EMailModel.EMailModel.subConversation`
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

    @staticmethod
    def createFromEmailBytes(
        emailBytes: bytes, mailbox: MailboxModel
    ) -> EMailModel | None:
        """Creates an :class:`core.models.EMailModel.EMailModel` from an email in bytes form.

        Args:
            emailBytes: The email bytes to parse the emaildata from.
            mailbox: The mailbox the email is in.

        Returns:
            The :class:`core.models.EMailModel.EMailModel` instance with data from the bytes.
            None if there is no Message-ID header in :attr:`emailMessage`,
                if the mail already exists in the db or
                if the mail is spam and is supposed to be thrown out.
        """
        emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)

        message_id = getHeader(
            emailMessage,
            HeaderFields.MESSAGE_ID,
            fallbackCallable=lambda: md5(emailBytes).hexdigest(),
        )
        x_spam = getHeader(
            emailMessage, HeaderFields.X_SPAM, fallbackCallable=lambda: ""
        )
        if is_X_Spam(x_spam) and get_config("THROW_OUT_SPAM"):
            logger.debug(
                "Skipping email with Message-ID %s in %s, it is flagged as spam.",
                message_id,
                mailbox,
            )
            return None

        if EMailModel.objects.filter(message_id=message_id, mailbox=mailbox).count():
            logger.debug(
                "Skipping email with Message-ID %s in %s, it already exists in the db.",
                message_id,
                mailbox,
            )
            return None

        new_email = EMailModel(message_id=message_id, mailbox=mailbox, x_spam=x_spam)
        new_email.datetime = parseDatetimeHeader(
            getHeader(emailMessage, HeaderFields.DATE)
        )
        new_email.email_subject = getHeader(
            emailMessage, HeaderFields.SUBJECT, fallbackCallable=lambda: ""
        )
        new_email.datasize = len(emailBytes)

        inReplyTo_message_id = getHeader(emailMessage, HeaderFields.IN_REPLY_TO)
        if inReplyTo_message_id:
            try:
                new_email.inReplyTo = EMailModel.objects.get(
                    message_id=inReplyTo_message_id
                )
            except EMailModel.DoesNotExist:
                new_email.inReplyTo = None

        new_email.mailinglist = MailingListModel.fromEmailMessage(emailMessage)

        headerDict = {}
        for headerName in emailMessage:
            headerDict[headerName] = getHeader(emailMessage, headerName)
        new_email.headers = headerDict

        new_email.plain_bodytext = ""
        new_email.html_bodytext = ""
        attachments = []
        for part in emailMessage.walk():
            contentType = part.get_content_type()
            contentDisposition = part.get_content_disposition()
            # The order in this switch is crucial
            # Rare email parts should be in the back
            if contentType == "text/plain":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset("utf-8")
                new_email.plain_bodytext += payload.decode(charset, errors="replace")
            elif contentType == "text/html":
                payload = part.get_payload(decode=True)
                charset = part.get_content_charset("utf-8")
                new_email.html_bodytext += payload.decode(charset, errors="replace")
            elif contentDisposition in ["inline", "attachment"] or (
                any(
                    contentType.startswith(type_to_save)
                    for type_to_save in get_config("SAVE_CONTENT_TYPE_PREFIXES")
                )
                and not any(
                    contentType.endswith(type_to_skip)
                    for type_to_skip in get_config("DONT_SAVE_CONTENT_TYPE_SUFFIXES")
                )
            ):
                attachments.append(
                    (AttachmentModel.fromData(part, email=new_email), part)
                )
            else:
                logger.debug(
                    "Part %s with disposition %s of email %s was not parsed.",
                    contentType,
                    contentDisposition,
                    new_email.message_id,
                )
        logger.debug("Successfully parsed email.")
        try:
            with transaction.atomic():
                if new_email.mailinglist:
                    new_email.mailinglist.save()
                new_email.save(emailData=emailBytes)
                for mention in HeaderFields.Correspondents.values:
                    correspondentHeader = getHeader(emailMessage, mention)
                    if correspondentHeader:
                        EMailCorrespondentsModel.createFromHeader(
                            correspondentHeader, mention, new_email
                        )
                for attachment, data in attachments:
                    attachment.save(attachmentData=data)
        except Exception:
            logger.exception(
                "Failed creating email from bytes: Error while saving email to db!"
            )
            return None
        return new_email

    @override
    @property
    def has_download(self):
        return self.eml_filepath is not None

    @override
    @property
    def has_thumbnail(self):
        return self.html_filepath is not None
