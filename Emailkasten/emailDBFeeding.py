# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Provides functions for inserting data from the mails and their environment into the database.
Functions starting with _ are helpers and are used only within the scope of this module.

Functions:
    :func:`_insertCorrespondent`: Writes the given data of a correspondent to the database.
    :func:`_insertEMailCorrespondent`: Writes the connection betweeen an email and a correspondent to the database.
    :func:`_insertAttachment`: Writes the given data for an attachment to the database.
    :func:`_insertImage`: Writes the given data for an image to the database.
    :func:`_insertMailinglist`: Writes the given data for an mailingslist served by a existing correspondent to database.
    :func:`insertMailbox`: Writes the given data for a mailbox of an account to database.
    :func:`insertEMail`: Writes the given data for an email to database.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import django.db

from .constants import ParsedMailKeys
from .Models.AttachmentModel import AttachmentModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.DaemonModel import DaemonModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .Models.EMailModel import EMailModel
from .Models.ImageModel import ImageModel
from .Models.MailboxModel import MailboxModel
from .Models.MailingListModel import MailingListModel

if TYPE_CHECKING:
    from typing import Any

    from .Models.AccountModel import AccountModel


logger = logging.getLogger(__name__)


def _insertCorrespondent(correspondentData: tuple[str,str]) -> CorrespondentModel:
    """Writes the given data of a correspondent to the database.
    If a correspondent with that address already exists, updates the name field if it is blank.

    Args:
        correspondentData: Data of the correspondent to be inserted, as created by :func:`Emailkasten.mailParsing.parseCorrespondent`.

    Returns:
        The entry to the correspondent from the database.
    """
    logger.debug("Creating entry for correspondent in DB...")

    correspondentEntry, created  = CorrespondentModel.objects.get_or_create(
        email_address = correspondentData[1],
        defaults = {'email_name': correspondentData[0]}
    )
    if created:
        logger.debug("Entry for %s created", str(correspondentEntry))
    else:
        logger.debug("Entry for %s already exists", str(correspondentEntry))
        if not correspondentEntry.email_name and correspondentData[0]:
            logger.debug("EMailName field of %s is blank, update it ... ", str(correspondentEntry))
            correspondentEntry.email_name = correspondentData[0]
            correspondentEntry.save()
            logger.debug("Successfully updated emailName of %s.", str(correspondentEntry))

    return correspondentEntry



def _insertEMailCorrespondent(emailEntry: EMailModel, correspondentEntry: CorrespondentModel, mention: str) -> None:
    """Writes the connection betweeen an email and a correspondent to the database.
    If that entry already exists does nothing.

    Args:
        emailEntry: The database entry of the mail that names the correspondent.
        correspondentEntry: The database entry of the correspondent to connect to the mails entry.
        mention: The mention type of the correspondent in the mail. Must be one of :class:`Emailkasten.constants.ParsedMailKeys.Correspondent`.
    """
    logger.debug("Creating entry for %s correspondent in DB...", mention)

    emailCorrespondentsEntry, created = EMailCorrespondentsModel.objects.get_or_create(
        email = emailEntry,
        correspondent = correspondentEntry,
        mention = mention
    )
    if created:
        logger.debug("Successfully created entry for %s.", str(emailCorrespondentsEntry))
    else:
        logger.debug("Entry for %s already exists", str(emailCorrespondentsEntry))



def _insertAttachment(attachmentData: dict[str,Any], emailEntry: EMailModel) -> None:
    """Writes the given data for an attachment to the database.
    If that entry already exists does nothing.

    Args:
        attachmentData: The data of the attachment to be inserted, as created by :func:`Emailkasten.mailParsing.parseAttachment`.
        emailEntry: The database entry of the mail that the attachment is part of.
    """
    attachmentEntry, created  = AttachmentModel.objects.get_or_create(
        file_path = attachmentData[ParsedMailKeys.Attachment.FILE_PATH],
        email = emailEntry,
        defaults = {
            'file_name' : attachmentData[ParsedMailKeys.Attachment.FILE_NAME],
            'datasize' : attachmentData[ParsedMailKeys.Attachment.SIZE]
        }
    )
    if created:
        logger.debug("Successfully created entry for %s.", str(attachmentEntry))
    else:
        logger.debug("Entry for %s already exists", str(attachmentEntry))



def _insertImage(imageData: dict[str,Any], emailEntry: EMailModel) -> None:
    """Writes the given data for an image to the database.
    If that entry already exists does nothing.

    Args:
        imageData: The data of the image to be inserted, as created by :func:`Emailkasten.mailParsing.parseImage`.
        emailEntry: The database entry of the mail that the image is part of.
    """
    imageEntry, created  = ImageModel.objects.get_or_create(
        file_path = imageData[ParsedMailKeys.Image.FILE_PATH],
        email = emailEntry,
        defaults = {
            'file_name' : imageData[ParsedMailKeys.Image.FILE_NAME],
            'datasize' : imageData[ParsedMailKeys.Image.SIZE]
        }
    )
    if created:
        logger.debug("Successfully created entry for %s.", str(imageEntry))
    else:
        logger.debug("Entry for %s already exists", str(imageEntry))



def _insertMailinglist(mailinglistData: dict[str,Any], fromCorrespondentEntry: CorrespondentModel) -> MailingListModel|None:
    """Writes the given data for an mailingslist served by a existing correspondent to database.
    If that entry already exists does nothing. If the mailinglist has no ID, it will not be saved.

    Args:
        mailinglistData: The data of the mailinglist to be inserted, as created by :func:`Emailkasten.mailParsing.parseMailinglist`.
        fromCorrespondentEntry: The database entry of the correspondent that serves the mailinglist.

    Returns:
        The database entry of the mailinglist, either newly created or retrieved.
    """
    mailinglistEntry = None
    if mailinglistData[ParsedMailKeys.MailingList.ID]:

        logger.debug("Creating entry for mailinglist in DB...")
        mailinglistEntry, created = MailingListModel.objects.get_or_create(
                list_id = mailinglistData[ParsedMailKeys.MailingList.ID],
                correspondent = fromCorrespondentEntry,
                defaults= {
                    'list_owner': mailinglistData[ParsedMailKeys.MailingList.OWNER],
                    'list_subscribe': mailinglistData[ParsedMailKeys.MailingList.SUBSCRIBE],
                    'list_unsubscribe': mailinglistData[ParsedMailKeys.MailingList.UNSUBSCRIBE],
                    'list_post': mailinglistData[ParsedMailKeys.MailingList.POST],
                    'list_help': mailinglistData[ParsedMailKeys.MailingList.HELP],
                    'list_archive': mailinglistData[ParsedMailKeys.MailingList.ARCHIVE],
                }
            )
        if created:
            logger.debug("Successfully created entry for %s.", str(mailinglistEntry))
        else:
            logger.debug("Mailinglist entry already exists")
    else:
        logger.debug("No mailinglist ID found, not writing to DB")

    return mailinglistEntry



def insertMailbox(mailboxData: str, account: AccountModel) -> None:
    """Writes the given data for a mailbox of an account to database.
    If a new entry is created, adds a new daemon entry for that mailbox as well. If any of the database operations fails, discards all changes to ensure data integrity.
    If the entry for the mailbox already exists does nothing.

    Args:
        mailboxData: The name of the mailbox to be inserted, as created by :func:`Emailkasten.mailParsing.parseMailbox`.
        account: The database entry of the account that the mailbox belongs to.
    """
    logger.debug("Saving mailbox %s from %s to db ...", mailboxData, str(account))
    try:
        with django.db.transaction.atomic():

            mailboxEntry, created = MailboxModel.objects.get_or_create(
                name = mailboxData,
                account = account
            )
            if created:
                logger.debug("Entry for %s created", str(mailboxEntry))
            else:
                logger.debug("Entry for %s already exists", str(mailboxEntry))

    except django.db.IntegrityError:
        logger.error("Error while writing to database, rollback to last state", exc_info=True)

    logger.debug("Successfully saved mailbox to db ...")



def insertEMail(emailData: dict[str,Any], account: AccountModel) -> None:
    """Writes the given data for an email to database.
    If that entry already exists does nothing. If any of the database operations fails, discards all changes to ensure data integrity.

    Args:
        emailData: The data of the mail to be inserted, as created by :func:`Emailkasten.mailParsing.parseMail`.
        account: The database entry of the account that the mail was found in.
    """
    logger.debug("Saving mail with subject %s from %s to db ...", emailData[ParsedMailKeys.Header.SUBJECT], emailData[ParsedMailKeys.Header.DATE])
    try:
        with django.db.transaction.atomic():

            # the FROM correspondent insertion has to be split to be able to add the FROM correspondent to an eventual mailinglist
            fromCorrespondent = emailData[ParsedMailKeys.Correspondent.FROM]
            fromCorrespondentEntry = None
            if fromCorrespondent:
                logger.debug("Adding FROM correspondent to DB...")

                fromCorrespondentEntry = _insertCorrespondent(fromCorrespondent[0]) #there should only be one from correspondent
            else:
                logger.error("No FROM Correspondent found in mail, not writing to DB!")



            mailinglistEntry = None
            if emailData[ParsedMailKeys.MAILINGLIST] and fromCorrespondentEntry:
                mailinglistEntry = _insertMailinglist(emailData[ParsedMailKeys.MAILINGLIST], fromCorrespondentEntry)
            else:
                logger.debug("No mailinglist info found in mail, not writing to DB")



            inReplyToMailEntry = None
            if emailData[ParsedMailKeys.Header.IN_REPLY_TO]:
                logger.debug("Querying inReplyTo mail ...")
                try:
                    inReplyToMailEntry = EMailModel.objects.get(message_id = emailData[ParsedMailKeys.Header.IN_REPLY_TO])

                    logger.debug("Successfully retrieved inReplyTo mail.")
                except EMailModel.DoesNotExist:
                    logger.warning("Could not find inReplyTo mail %s!", emailData[ParsedMailKeys.Header.IN_REPLY_TO])
            else:
                logger.debug("No In-Reply-To found in mail, not writing to DB")



            logger.debug("Creating entry for email in DB...")

            emailEntry, created = EMailModel.objects.get_or_create(
                message_id = emailData[ParsedMailKeys.Header.MESSAGE_ID],
                defaults = {
                    'account' : account,
                    'mailinglist': mailinglistEntry,
                    'inReplyTo' : inReplyToMailEntry,
                    'bodytext' : emailData[ParsedMailKeys.BODYTEXT],
                    'datasize' :  emailData[ParsedMailKeys.SIZE],
                    'eml_filepath' : emailData[ParsedMailKeys.EML_FILE_PATH],
                    'prerender_filepath': emailData[ParsedMailKeys.PRERENDER_FILE_PATH],
                    'datetime' : emailData[ParsedMailKeys.Header.DATE],
                    'email_subject' : emailData[ParsedMailKeys.Header.SUBJECT],
                    'comments': emailData[ParsedMailKeys.Header.COMMENTS],
                    'keywords': emailData[ParsedMailKeys.Header.KEYWORDS],
                    'importance': emailData[ParsedMailKeys.Header.IMPORTANCE],
                    'priority': emailData[ParsedMailKeys.Header.PRIORITY],
                    'precedence': emailData[ParsedMailKeys.Header.PRECEDENCE],
                    'received': emailData[ParsedMailKeys.Header.RECEIVED],
                    'user_agent': emailData[ParsedMailKeys.Header.USER_AGENT],
                    'auto_submitted': emailData[ParsedMailKeys.Header.AUTO_SUBMITTED],
                    'content_type': emailData[ParsedMailKeys.Header.CONTENT_TYPE],
                    'content_language': emailData[ParsedMailKeys.Header.CONTENT_LANGUAGE],
                    'content_location': emailData[ParsedMailKeys.Header.CONTENT_LOCATION],
                    'x_priority': emailData[ParsedMailKeys.Header.X_PRIORITY],
                    'x_originated_client': emailData[ParsedMailKeys.Header.X_ORIGINATING_CLIENT],
                    'x_spam': emailData[ParsedMailKeys.Header.X_SPAM_FLAG]
                }
            )
            if created:
                logger.debug("Successfully created entry for %s.", str(emailEntry))
            else:
                logger.debug("Entry for %s already exists", str(emailEntry))



            if emailData[ParsedMailKeys.ATTACHMENTS]:
                logger.debug("Creating entries for attachments in DB...")

                for attachmentData in emailData[ParsedMailKeys.ATTACHMENTS]:
                    _insertAttachment(attachmentData, emailEntry)

                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No attachment files found in mail, not writing to DB")



            if emailData[ParsedMailKeys.IMAGES]:
                logger.debug("Creating entries for images in DB...")

                for imageData in emailData[ParsedMailKeys.IMAGES]:
                    _insertImage(imageData, emailEntry)

                logger.debug("Successfully added images to DB.")
            else:
                logger.debug("No images found in mail, not writing to DB")



            for mentionType, correspondentHeader in ParsedMailKeys.Correspondent():
                if correspondentHeader == ParsedMailKeys.Correspondent.FROM:   # from correspondent has been added earlier, just add the connection to bridge table here
                    if fromCorrespondentEntry:

                        _insertEMailCorrespondent(emailEntry, fromCorrespondentEntry, mentionType)

                        logger.debug("Successfully added entries for %s correspondent to DB.", mentionType)
                    else:
                        logger.error("No %s correspondent found in mail, not writing to DB!", mentionType)

                else:
                    if emailData[correspondentHeader]:
                        logger.debug("Creating entry for %s correspondents in DB...", mentionType)

                        for correspondentData in emailData[correspondentHeader]:
                            correspondentEntry = _insertCorrespondent(correspondentData)
                            _insertEMailCorrespondent(emailEntry, correspondentEntry, mentionType)

                        logger.debug("Successfully added entries for %s correspondents to DB.", mentionType)
                    else:
                        if mentionType == ParsedMailKeys.Correspondent.TO:
                            logger.warning("No %s correspondent found in mail, not writing to DB!", mentionType)
                        else:
                            logger.debug("No %s correspondent found in mail, not writing to DB!", mentionType)


    except django.db.IntegrityError:
        logger.error("Error while writing to database, rollback to last state", exc_info=True)

    logger.debug("Successfully saved mail to db.")
