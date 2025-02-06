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

from core import constants
from core.constants import ParsedMailKeys
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.utils.fileManagment import saveStore
from Emailkasten.utils import get_config

from ..utils.mailParsing import getDatetimeHeader, getHeader
from .AttachmentModel import AttachmentModel
from .ImageModel import ImageModel
from .MailingListModel import MailingListModel
from .StorageModel import StorageModel

if TYPE_CHECKING:
    from email.message import EmailMessage
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

    bodytext = models.TextField()
    """The plain bodytext of the mail."""

    # html_bodytext = models.TextField()
    # """The html bodytext of the mail."""

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

    comments = models.CharField(max_length=255, null=True)
    """The comments header of this mail. Can be null."""

    keywords = models.CharField(max_length=255, null=True)
    """The keywords header of this mail. Can be null."""

    importance = models.CharField(max_length=255, null=True)
    """The importance header of this mail. Can be null."""

    priority = models.CharField(max_length=255, null=True)
    """The priority header of this mail. Can be null."""

    precedence = models.CharField(max_length=255, null=True)
    """The precedence header of this mail. Can be null."""

    received = models.TextField(null=True)
    """The received header of this mail. Can be null."""

    user_agent = models.CharField(max_length=255, null=True)
    """The user_agent header of this mail. Can be null."""

    auto_submitted = models.CharField(max_length=255, null=True)
    """The auto_submitted header of this mail. Can be null."""

    content_type = models.CharField(max_length=255, null=True)
    """The content_type header of this mail. Can be null."""

    content_language = models.CharField(max_length=255, null=True)
    """The content_language header of this mail. Can be null."""

    content_location = models.CharField(max_length=255, null=True)
    """The content_location header of this mail. Can be null."""

    x_priority = models.CharField(max_length=255, null=True)
    """The x_priority header of this mail. Can be null."""

    x_originated_client = models.CharField(max_length=255, null=True)
    """The x_originated_client header of this mail. Can be null."""

    x_spam = models.CharField(max_length=255, null=True)
    """The x_spam header of this mail. Can be null."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.datetime} with subject {self.email_subject} from {str(self.account)}"

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
                    "Successfully removed the image file from storage.", exc_info=True
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
                    "Successfully removed the image file from storage.", exc_info=True
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
            return None
        super().save(*args, **kwargs)
        if "emailData" in kwargs and get_config("SAVE_TO_EML"):
            self.save_to_storage(kwargs["emailData"])

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
            logger.debug("Email %s is already stored as eml.", self)
            return

        @saveStore
        def writeMessageToEML(emlFile: BufferedWriter, emailData) -> None:
            emlGenerator = email.generator.BytesGenerator(emlFile)
            emlGenerator.flatten(emailData)

        logger.debug("Storing images %s ...", self)

        dirPath = StorageModel.getSubdirectory(self.message_id)
        preliminary_file_path = os.path.join(dirPath, self.message_id + ".eml")

        self.eml_filepath = writeMessageToEML(preliminary_file_path, emailData)
        self.save(update_fields=["eml_filepath"])

        logger.debug("Successfully stored image.")

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
        emailMessage: EmailMessage = email.parser.BytesParser(
            policy=policy.default
        ).parsebytes(emailBytes)

        message_id = getHeader(
            emailMessage,
            ParsedMailKeys.Header.MESSAGE_ID,
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
        new_email.datetime = getDatetimeHeader(emailMessage)
        new_email.email_subject = getHeader(emailMessage, ParsedMailKeys.Header.SUBJECT)
        new_email.datasize = len(emailBytes)
        if inReplyTo_message_id := getHeader(
            emailMessage, ParsedMailKeys.Header.IN_REPLY_TO
        ):
            try:
                new_email.inReplyTo = EMailModel.objects.get(
                    message_id=inReplyTo_message_id
                )
            except EMailModel.DoesNotExist:
                new_email.inReplyTo = None
        new_email.comments = getHeader(emailMessage, ParsedMailKeys.Header.COMMENTS)
        new_email.keywords = getHeader(emailMessage, ParsedMailKeys.Header.KEYWORDS)
        new_email.importance = getHeader(emailMessage, ParsedMailKeys.Header.IMPORTANCE)
        new_email.priority = getHeader(emailMessage, ParsedMailKeys.Header.PRIORITY)
        new_email.precedence = getHeader(emailMessage, ParsedMailKeys.Header.PRECEDENCE)
        new_email.received = getHeader(
            emailMessage, ParsedMailKeys.Header.RECEIVED, joiningString="\n"
        )
        new_email.user_agent = getHeader(emailMessage, ParsedMailKeys.Header.USER_AGENT)
        new_email.auto_submitted = getHeader(
            emailMessage, ParsedMailKeys.Header.AUTO_SUBMITTED
        )
        new_email.content_type = getHeader(
            emailMessage, ParsedMailKeys.Header.CONTENT_TYPE
        )
        new_email.content_language = getHeader(
            emailMessage, ParsedMailKeys.Header.CONTENT_LANGUAGE
        )
        new_email.content_location = getHeader(
            emailMessage, ParsedMailKeys.Header.CONTENT_LOCATION
        )
        new_email.x_priority = getHeader(emailMessage, ParsedMailKeys.Header.X_PRIORITY)
        new_email.x_originated_client = getHeader(
            emailMessage, ParsedMailKeys.Header.X_ORIGINATING_CLIENT
        )
        new_email.x_spam = getHeader(emailMessage, ParsedMailKeys.Header.X_SPAM_FLAG)

        new_email.mailinglist = MailingListModel.fromMessage(emailMessage)
        emailCorrespondents = []
        for mention in ParsedMailKeys.Correspondent():
            correspondentHeader = getHeader(emailMessage, mention)
            if correspondentHeader:
                for header in correspondentHeader.split(","):
                    emailCorrespondents.append(
                        EMailCorrespondentsModel.fromHeader(header, mention)
                    )
                    if correspondentHeader == ParsedMailKeys.Correspondent.FROM:
                        new_email.mailinglist.correspondent = emailCorrespondents[-1]

        new_email.bodytext = ""
        # new_email.html_bodytext = ""
        attachments = {}
        images = {}

        for part in emailMessage.walk():
            contentType = part.get_content_type()
            contentDisposition = part.get_content_disposition()
            # The order in this switch is crucial
            # Rare email parts should be in the back
            if contentType == "text/plain":
                payload = part.get_payload(decode=True)
                encoding = part.get_content_charset("utf-8")
                new_email.bodytext += payload.decode(encoding, errors="replace")
            # elif contentType == "text/html":
            #     payload = part.get_payload(decode=True)
            #     encoding = part.get_content_charset("utf-8")
            #     new_email.html_bodytext += payload.decode(encoding, errors="replace")
            # attachments must be before images to avoid doubling
            elif contentDisposition == "attachment":
                attachments[AttachmentModel.fromData(part, email=new_email)] = part
            elif contentType.startswith("image/"):
                images[ImageModel.fromData(part, email=new_email)] = part
            elif contentType in constants.ParsingConfiguration.APPLICATION_TYPES:
                attachments[AttachmentModel.fromData(part, email=new_email)] = part
            else:
                logger.debug(
                    "Part %s with disposition %s of email %s were not parsed.",
                    contentType,
                    contentDisposition,
                    new_email.message_id,
                )
        logger.debug("Successfully parsed email.")
        try:
            with transaction.atomic():
                for emailCorrespondent in emailCorrespondents:
                    if emailCorrespondent:
                        emailCorrespondent.correspondent.save()
                if new_email.mailinglist:
                    new_email.mailinglist.save()
                new_email.save(emailData=emailBytes)
                for emailCorrespondent in emailCorrespondents:
                    if emailCorrespondent:
                        emailCorrespondent.save()
                for attachment, data in attachments.items():
                    attachment.save(attachmentData=data)
                for image, data in images.items():
                    image.save(imageData=data)
        except Exception:
            return None
        return new_email
