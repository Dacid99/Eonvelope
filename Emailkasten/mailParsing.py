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


"""Provides functions for parsing features from the maildata.
Functions starting with _ are helpers and are used only within the scope of this module.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import datetime
import email
import email.header
import email.message
import email.utils
import logging
from typing import TYPE_CHECKING

import email_validator
from imap_tools.imap_utf7 import utf7_decode

from .constants import ParsedMailKeys, ParsingConfiguration

if TYPE_CHECKING:
    from typing import Any


logger = logging.getLogger(__name__)


def _decodeText(text: email.message.Message) -> str:
    """Decodes a text encoded as bytes.
    Checks for a specific charset to use.
    If none is found uses :attr:`Emailkasten.constants.ParsingConfiguration.CHARSET_DEFAULT`.

    Args:
        text: The text in bytes format to decode properly.

    Returns:
        The decoded text. Blank if none is present.
    """
    charset = text.get_content_charset() or ParsingConfiguration.CHARSET_DEFAULT
    if isinstance(textPayload := text.get_payload(decode=True), bytes):
        return textPayload.decode(charset, errors='replace')
    else:
        return ""


def _decodeHeader(header: str) -> str:
    """Decodes an email header field encoded as bytes.
    Checks for a specific charset to use.
    If none is found uses the default :attr:`Emailkasten.constants.MailParsingConfiguration.CHARSET_DEFAULT`.

    Note:
        Uses :func:`email.header.decode_header`.

    Args:
        header: The mail header to decode.

    Returns:
        The decoded mail header.
    """
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if not charset:
            decodedString += (
                fragment.decode(ParsingConfiguration.CHARSET_DEFAULT, errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )
        else:
            decodedString += (
                fragment.decode(charset, errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )

    return decodedString


def _separateRFC2822MailAddressFormat(mailers: list[str]) -> list[tuple[str,str]]:
    """Splits the RFC2822 address fiels into the mailer name mail address.

    Note:
        Uses :func:`email.utils.getaddresses` to seperate and :func:`email_validator.validate_email` to validate.

    Todo:
        If no valid mailaddress is found uses the entire address as fallback.

    Args:
        mailers: A list of address fields to seperate.

    Returns:
        A list of mailernames and mailaddresses
    """
    decodedMailers = [_decodeHeader(mailer) for mailer in mailers]
    mailAddresses = email.utils.getaddresses(decodedMailers)
    separatedMailers = []
    for mailName, mailAddress in mailAddresses:
        try:
            email_validator.validate_email(mailAddress, check_deliverability=False)
        except email_validator.EmailNotValidError:
            logger.warning("Mailaddress is invalid for %s, %s!", mailName, mailAddress)

        separatedMailers.append( (mailName, mailAddress) )
    return separatedMailers


def _parseMessageID(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the messageID header of the given mailmessage.
    If none is found uses the hash of the mailmessage as a fallback.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing MessageID ...")
    messageID = mailMessage.get(ParsedMailKeys.Header.MESSAGE_ID)
    if not messageID:
        logger.warning("No messageID found in mail, resorting to hash!")
        messageID = str(hash(mailMessage))
    else:
        logger.debug("Successfully parsed messageID")
    parsedMail[ParsedMailKeys.Header.MESSAGE_ID] = messageID


def _parseDate(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the date header of the given mailmessage.
    If none is found uses :attr:`Emailkasten.constants.ParsingConfiguration.DATE_DEFAULT` as fallback.
    The result is included in the parsedMail dict.

    Note:
        Uses :func:`email.utils.parsedate_to_datetime`.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing date ...")
    date = mailMessage.get(ParsedMailKeys.Header.DATE)
    if not date:
        logger.warning("No DATE found in mail, resorting to default!")
        parsedDate = datetime.datetime.strptime(ParsingConfiguration.DATE_DEFAULT, ParsingConfiguration.DATE_FORMAT)
    else:
        parsedDate = email.utils.parsedate_to_datetime(_decodeHeader(date))
    parsedMail[ParsedMailKeys.Header.DATE] = parsedDate



def _parseSubject(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the subject header of the given mailmessage.
    If there is no such header, falls back to a blank string.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing subject ...")
    if subject := mailMessage.get(ParsedMailKeys.Header.SUBJECT):
        decodedSubject = _decodeHeader(subject)
        if ParsingConfiguration.STRIP_TEXTS:
            parsedSubject = decodedSubject.strip()
        else:
            parsedSubject = decodedSubject
        logger.debug("Successfully parsed subject")
    else:
        logger.warning("No SUBJECT found in mail!")
        parsedSubject = ""
    parsedMail[ParsedMailKeys.Header.SUBJECT] = parsedSubject



def _parseBodyText(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the bodytext of the given mailmessage.
    Combines all elements of content type text if the message is multipart. Otherwise uses the full message.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing bodytext ...")
    mailBodyText = ""
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition():
                continue
            if part.get_content_type().startswith('text/'):
                mailBodyText += _decodeText(part)
    else:
        mailBodyText = _decodeText(mailMessage)
    if mailBodyText == "":
        logger.warning("No BODYTEXT found in mail!")
    else:
        logger.debug("Successfully parsed bodytext")

    if ParsingConfiguration.STRIP_TEXTS:
        parsedBodyText = mailBodyText.strip()
        logger.debug("Stripped bodytext")
    else:
        parsedBodyText = mailBodyText

    parsedMail[ParsedMailKeys.BODYTEXT] = parsedBodyText



def _parseImages(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the inline images in the given mailmessage.
    Looks for elements of content type image that are not an attachment.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        A list of images in the mailmessage.
        Empty if none are found or the message is not multipart.


    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing images ...")
    images = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type().startswith('image/'):
                # imageFileName = part.get_filename()
                # if not imageFileName:
                #     imageFileName =
                imagesDict: dict[str,Any] = {}
                imagesDict[ParsedMailKeys.Image.DATA] = part
                imagesDict[ParsedMailKeys.Image.SIZE] = len(part.as_bytes())
                imagesDict[ParsedMailKeys.Image.FILE_NAME] = part.get_filename()
                imagesDict[ParsedMailKeys.Image.FILE_PATH] = None

                images.append(imagesDict)

    if not images:
        logger.debug("No images found in mail")
    else:
        logger.debug("Successfully parsed images")

    parsedMail[ParsedMailKeys.IMAGES] = images



def _parseAttachments(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the attachments in the given mailmessage.
    Looks for elements with content disposition attachment or
    content type in :attr:`Emailkasten.ParsingConfiguration.APPLICATION_TYPES`.
    If no filename is found for a file uses the hash +.attachment.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing attachments ...")
    attachments = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if ( part.get_content_disposition() == "attachment"
                 or part.get_content_type() in ParsingConfiguration.APPLICATION_TYPES):
                attachmentDict: dict[str, Any] = {}
                attachmentDict[ParsedMailKeys.Attachment.DATA] = part
                attachmentDict[ParsedMailKeys.Attachment.SIZE] = len(part.as_bytes())
                attachmentDict[ParsedMailKeys.Attachment.FILE_NAME] = part.get_filename() or f"{hash(part)}.attachment"
                attachmentDict[ParsedMailKeys.Attachment.FILE_PATH] = None

                attachments.append(attachmentDict)

    if not attachments:
        logger.debug("No attachments found in mail")
    else:
        logger.debug("Successfully parsed attachments")

    parsedMail[ParsedMailKeys.ATTACHMENTS] = attachments



def _parseHeader(mailMessage: email.message.Message, headerKey: str, parsedMail: dict):
    """Parses the given header of the given mailmessage.
    The result is included in the parsedMail dict.

    Note:
        For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.

    Args:
        mailMessage: The mailmessage to be parsed.
        headerKey: The header to extract from the message.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        The parsed header of the mailmessage.
        Empty if there is no such header.


    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing %s ...", headerKey)
    header = mailMessage.get(headerKey, "")
    if not header:
        logger.debug("No %s found in mail.", headerKey)
    else:
        logger.debug("Successfully parsed %s", headerKey)
    parsedMail[headerKey] = header



def _parseMultipleHeader(mailMessage: email.message.Message, headerKey: str, parsedMail: dict):
    """Parses the given header, which may appear multiple times, of the given mailmessage.
    The combination of the results is included in the parsedMail dict.

    Todo:
        Can be optimized.

    Args:
        mailMessage: The mailmessage to be parsed.
        headerKey: The header to extract from the message.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing %s ...", headerKey)
    headers = mailMessage.get_all(headerKey, '')
    combinedHeaders = "\n".join(headers)
    if combinedHeaders:
        logger.debug("Successfully parsed %s", headerKey)
    else:
        logger.debug("No %s found in mail.", headerKey)
    parsedMail[headerKey] = combinedHeaders



def _parseMailinglist(mailMessage: email.message.Message, parsedMail: dict):
    """Parses the mailinglist headers of the given mailmessage.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    mailinglistDict: dict = {}
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.ID, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.OWNER, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.SUBSCRIBE, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.UNSUBSCRIBE, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.POST, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.HELP, mailinglistDict)
    _parseHeader(mailMessage, ParsedMailKeys.MailingList.ARCHIVE, mailinglistDict)

    parsedMail[ParsedMailKeys.MAILINGLIST] = mailinglistDict



def _parseCorrespondents(mailMessage: email.message.Message, mentionHeaderKey: str, parsedMail: dict):
    """Parses the correspondents that are mentioned in a given way.
    The result is included in the parsedMail dict.

    Args:
        mailMessage: The mailmessage to be parsed.
        mentionHeaderKey: The way the correspondents are mentioned, a member of :class:`Emailkasten.constants.ParsedMailKeys.Correspondent`.
        parsedMail: The dictionary storing the parsed mail features.

    Returns:
        None, the parsed header is appended to the parsedMail dict.
    """
    logger.debug("Parsing %s ...", mentionHeaderKey)
    correspondents = mailMessage.get_all(mentionHeaderKey)
    if not correspondents:
        logger.debug("No %s correspondents found in mail!", mentionHeaderKey)
        return []
    else:
        logger.debug("Successfully parsed %s correspondents.", mentionHeaderKey)

    parsedMail[mentionHeaderKey] = _separateRFC2822MailAddressFormat(correspondents)


def parseMail(mailToParse: bytes) -> dict[str, Any]:
    """Parses a mail returned by a mail server for its features.
    Uses the various private functions in :mod:`Emailkasten.mailParsing`.

    Todo:
        Use iteration over :class:`Emailkasten.constants.ParsedMailKeys` to keep it concise and safe.

    Args:
        mailToParse: The mail data as supplied by the mailhost.

    Returns:
        The features of the mail in a dictionary with keys as defined in :class:`Emailkasten.constants.ParsedMailKeys`.
    """
    mailMessage = email.message_from_bytes(mailToParse)

    logger.debug("Parsing email with messageID %s ...", mailMessage.get(ParsedMailKeys.Header.MESSAGE_ID))

    parsedEMail: dict[str, Any] = {}
    parsedEMail[ParsedMailKeys.DATA] = mailToParse
    parsedEMail[ParsedMailKeys.FULL_MESSAGE] = mailMessage
    parsedEMail[ParsedMailKeys.SIZE] = len(mailToParse)

    _parseMessageID(mailMessage, parsedEMail)
    _parseDate(mailMessage, parsedEMail)
    _parseSubject(mailMessage, parsedEMail)
    _parseDate(mailMessage, parsedEMail)
    _parseBodyText(mailMessage, parsedEMail)

    for _, correspondentHeader in ParsedMailKeys.Correspondent():
        _parseCorrespondents(mailMessage, correspondentHeader, parsedEMail)

    _parseAttachments(mailMessage, parsedEMail)
    _parseImages(mailMessage, parsedEMail)
    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = None
    parsedEMail[ParsedMailKeys.PRERENDER_FILE_PATH] = None

    _parseMailinglist(mailMessage, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.IN_REPLY_TO, parsedEMail)

    _parseHeader(mailMessage, ParsedMailKeys.Header.COMMENTS, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.LANGUAGE, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LANGUAGE, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_TYPE, parsedEMail)

    _parseHeader(mailMessage, ParsedMailKeys.Header.KEYWORDS, parsedEMail)
    _parseMultipleHeader(mailMessage, ParsedMailKeys.Header.RECEIVED, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.IMPORTANCE, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.PRIORITY, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.PRECEDENCE, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LOCATION, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.ARCHIVED_AT, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.USER_AGENT, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.X_PRIORITY, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.X_ORIGINATING_CLIENT, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.X_SPAM_FLAG, parsedEMail)
    _parseHeader(mailMessage, ParsedMailKeys.Header.AUTO_SUBMITTED, parsedEMail)

    logger.debug("Successfully parsed mail")
    return parsedEMail


def parseMailbox(mailboxBytes: bytes) -> str:
    """Parses the mailbox name as received by the scanMailboxes method in :mod:`Emailkasten.Fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.

    Args:
        mailboxBytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The name of the mailbox independent of its parent folders
    """
    mailbox = utf7_decode(mailboxBytes)
    mailboxName = mailbox.split("\"/\"")[1].strip()
    if mailboxName == "":
        mailboxName = mailbox.split("\" \"")[1].strip()
    return mailboxName
