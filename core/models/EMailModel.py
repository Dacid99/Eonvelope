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

import email.generator
import email.parser
import logging
import os
from email import policy
from hashlib import md5
from typing import TYPE_CHECKING

from django.db import models, transaction

from core.constants import CORRESPONDENT_HEADERS, HeaderFields
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.utils.fileManagment import saveStore
from Emailkasten.utils import get_config

from ..utils.mailParsing import getHeader, parseDatetimeHeader
from .AttachmentModel import AttachmentModel
from .MailingListModel import MailingListModel
from .StorageModel import StorageModel

if TYPE_CHECKING:
    from io import BufferedWriter

    from .AccountModel import AccountModel
    from .CorrespondentModel import CorrespondentModel


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class EMailModel(models.Model):
    """Database model for an email."""

    message_id = models.CharField(max_length=255)
    """The messageID header of the mail. Unique together with :attr:`account`."""

    datetime = models.DateTimeField()
    """The Date header of the mail."""

    email_subject = models.CharField(max_length=255, null=True)
    """The subject header of the mail."""

    plain_bodytext = models.TextField()
    """The plain bodytext of the mail."""

    html_bodytext = models.TextField()
    """The html bodytext of the mail."""

    inReplyTo: models.ForeignKey[EMailModel] = models.ForeignKey(
        "self", null=True, related_name="replies", on_delete=models.SET_NULL
    )
    """The mail that this mail is a response to. Can be null. Deletion of that replied-to mail sets this field to NULL."""

    datasize = models.IntegerField()
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

    prerender_filepath = models.FilePathField(
        path=get_config("STORAGE_PATH"),
        max_length=255,
        recursive=True,
        match=rf".*\.{get_config('PRERENDER_IMAGETYPE')}$",
        null=True,
    )
    """The path where the prerender image of the mail is stored.
    Can be null if the prerendering process was no successful.
    Must contain :attr:`constance.get_config('STORAGE_PATH')` and end on :attr:`constance.get_config('PRERENDER_IMAGETYPE')`.
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

    account: models.ForeignKey[AccountModel] = models.ForeignKey(
        "AccountModel", related_name="emails", on_delete=models.CASCADE
    )
    """The account that this mail has been found in. Unique together with :attr:`message_id`. Deletion of that `account` deletes this mail."""

    headers = models.JSONField(null=True)
    """All other header fields of the mail. Can be null."""

    x_spam = models.CharField(max_length=255, null=True)
    """The x_spam header of this mail. Can be null."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.datetime} from {str(self.account)}"

    class Meta:
        """Metadata class for the model."""

        db_table = "emails"
        """The name of the database table for the emails."""

        constraints = [
            models.UniqueConstraint(
                fields=["message_id", "account"],
                name="email_unique_together_message_id_account",
            )
        ]
        """`message_id` and :attr:`account` in combination are unique."""

    def delete(self, *args, **kwargs):
        """Extended :django::func:`django.models.Model.delete` method
        to delete :attr:`eml_filepath` and :attr:`prerender_filepath` files on deletion.
        """
        super().delete(*args, **kwargs)

        if self.eml_filepath:
            logger.debug("Removing %s from storage ...", str(self))
            try:
                os.remove(self.eml_filepath)
                logger.debug(
                    "Successfully removed the eml file from storage.", exc_info=True
                )
            except FileNotFoundError:
                logger.error("%s was not found!", self.eml_filepath, exc_info=True)
            except OSError:
                logger.error(
                    "An OS error occured removing %s!",
                    self.eml_filepath,
                    exc_info=True,
                )
            except Exception:
                logger.error(
                    "An unexpected error occured removing %s!",
                    self.eml_filepath,
                    exc_info=True,
                )

        if self.prerender_filepath:
            logger.debug("Removing %s from storage ...", str(self))
            try:
                os.remove(self.prerender_filepath)
                logger.debug(
                    "Successfully removed the prerender image file from storage.",
                    exc_info=True,
                )
            except FileNotFoundError:
                logger.error(
                    "%s was not found!", self.prerender_filepath, exc_info=True
                )
            except OSError:
                logger.error(
                    "An OS error occured removing %s!",
                    self.prerender_filepath,
                    exc_info=True,
                )
            except Exception:
                logger.error(
                    "An unexpected error occured removing %s!",
                    self.prerender_filepath,
                    exc_info=True,
                )

    def save(self, *args, **kwargs):
        """Extended :django::func:`django.models.Model.save` method
        to throw out spam and save the data to eml if configured.
        """
        if self.isSpam() and get_config("THROW_OUT_SPAM"):
            return
        emailData = kwargs.pop("emailData", None)
        super().save(*args, **kwargs)
        if emailData is not None and get_config("DEFAULT_SAVE_TO_EML"):
            self.save_to_storage(emailData)

    def save_to_storage(self, emailData):
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
        def writeMessageToEML(emlFile: BufferedWriter, emailData) -> None:
            emlGenerator = email.generator.BytesGenerator(emlFile)
            emlGenerator.flatten(emailData)

        logger.debug("Storing %s as eml ...", self)

        dirPath = StorageModel.getSubdirectory(self.message_id)
        preliminary_file_path = os.path.join(dirPath, self.message_id + ".eml")
        if file_path := writeMessageToEML(preliminary_file_path, emailData):
            self.eml_filepath = file_path
            self.save(update_fields=["eml_filepath"])
            logger.debug("Successfully stored email as eml.")
        else:
            logger.error("Failed to store %s as eml!", self)

    def subConversation(self) -> list:
        subConversationEmails = [self]
        for replyEmail in self.replies.all():
            subConversationEmails.extend(replyEmail.subConversation())
        return subConversationEmails

    def fullConversation(self) -> list:
        rootEmail = self
        while rootEmail.inReplyTo:
            rootEmail = rootEmail.inReplyTo
        return rootEmail.subConversation()

    def isSpam(self) -> bool:
        """Checks the spam headers to decide whether the mail is spam.

        Returns:
            Whether the mail is considered spam.
        """
        return bool(self.x_spam) and self.x_spam != "NO"

    @staticmethod
    def createFromEmailBytes(
        emailBytes: bytes, account: AccountModel = None
    ) -> EMailModel | None:
        emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)
        message_id = getHeader(
            emailMessage,
            HeaderFields.MESSAGE_ID,
            lambda: md5(emailBytes).hexdigest(),
        )

        try:
            EMailModel.objects.get(message_id=message_id)
            logger.debug(
                "Skipping email with Message-ID %s, it already exists in the db.",
                message_id,
            )
            return None
        except EMailModel.DoesNotExist:
            logger.debug("Parsing email with Message-ID %s ...", message_id)

        new_email = EMailModel(message_id=message_id, account=account)
        new_email.datetime = parseDatetimeHeader(
            getHeader(emailMessage, HeaderFields.DATE)
        )
        new_email.email_subject = getHeader(emailMessage, HeaderFields.SUBJECT)
        new_email.datasize = len(emailBytes)
        if inReplyTo_message_id := getHeader(emailMessage, HeaderFields.IN_REPLY_TO):
            try:
                new_email.inReplyTo = EMailModel.objects.get(
                    message_id=inReplyTo_message_id
                )
            except EMailModel.DoesNotExist:
                new_email.inReplyTo = None

        new_email.x_spam = getHeader(emailMessage, HeaderFields.X_SPAM_FLAG)

        headerDict = {}
        for headerName in emailMessage.keys():
            headerDict[headerName] = getHeader(emailMessage, headerName)
        new_email.headers = headerDict

        new_email.mailinglist = MailingListModel.fromEmailMessage(emailMessage)
        emailCorrespondents = []
        for mention in CORRESPONDENT_HEADERS:
            correspondentHeader = getHeader(emailMessage, mention)
            if correspondentHeader:
                for header in correspondentHeader.split(","):
                    emailCorrespondents.append(
                        EMailCorrespondentsModel.fromHeader(
                            header, mention, email=new_email
                        )
                    )
                    if correspondentHeader == HeaderFields.Correspondent.FROM:
                        new_email.mailinglist.correspondent = emailCorrespondents[-1]

        new_email.plain_bodytext = ""
        new_email.html_bodytext = ""
        attachments = {}

        for part in emailMessage.walk():
            contentType = part.get_content_type()
            contentDisposition = part.get_content_disposition()
            # The order in this switch is crucial
            # Rare email parts should be in the back
            if contentType == "text/plain":
                payload = part.get_payload(decode=True)
                encoding = part.get_content_charset("utf-8")
                new_email.plain_bodytext += payload.decode(encoding, errors="replace")
            elif contentType == "text/html":
                payload = part.get_payload(decode=True)
                encoding = part.get_content_charset("utf-8")
                new_email.html_bodytext += payload.decode(encoding, errors="replace")
            elif contentDisposition is not None:
                attachments[AttachmentModel.fromData(part, email=new_email)] = part
            elif any(
                contentType.startswith(type_to_save)
                for type_to_save in get_config("SAVE_CONTENT_TYPE_PREFIXES")
            ) and not any(
                contentType.endswith(type_to_skip)
                for type_to_skip in get_config("DONT_SAVE_CONTENT_TYPE_SUFFIXES")
            ):
                attachments[AttachmentModel.fromData(part, email=new_email)] = part
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
                for emailCorrespondent in emailCorrespondents:
                    if emailCorrespondent is not None:
                        emailCorrespondent.correspondent.save()
                if new_email.mailinglist:
                    new_email.mailinglist.save()
                new_email.save(emailData=emailBytes)
                for emailCorrespondent in emailCorrespondents:
                    if emailCorrespondent is not None:
                        emailCorrespondent.save()
                for attachment, data in attachments.items():
                    attachment.save(attachmentData=data)
        except Exception:
            return None
        return new_email
