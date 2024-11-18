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

from .constants import ParsedMailKeys, ParsingConfiguration

if TYPE_CHECKING:
    from typing import Any


logger = logging.getLogger(__name__)


def _decodeText(text: email.message.Message) -> str:
    """Decodes a text encoded as bytes.
    Checks for a specific charset to use. If none is found uses the default :attr:`Emailkasten.constants.ParsingConfiguration.CHARSET_DEFAULT`.

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
    Uses the :python::func:`email.header.decode_header` function.
    Checks for a specific charset to use.
    If none is found uses the default :attr:`Emailkasten.constants.MailParsingConfiguration.CHARSET_DEFAULT`.

    Args:
        header: The mail header to decode.

    Returns:
        The decoded mail header.
    """
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if charset is None:
            decodedString += fragment.decode(ParsingConfiguration.CHARSET_DEFAULT, errors='replace') if isinstance(fragment, bytes) else fragment
        else:
            decodedString += fragment.decode(charset, errors='replace') if isinstance(fragment, bytes) else fragment

    return decodedString


def _separateRFC2822MailAddressFormat(mailers: list[str]) -> list[tuple[str,str]]:
    """Splits the RFC2822 address fiels into the mailer name mail address.
    Uses :func:`email.utils.getaddresses` to seperate and :python::func:`email_validator.validate_email` to validate.
    TODO: If no valid mailaddress is found uses the entire address as fallback.

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


def _parseMessageID(mailMessage: email.message.Message) -> str:
    """Parses the messageID header of the given mailmessage.
    If none is found uses the hash of the mailmessage as a fallback.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        The messageID header of the mailmessage.
        If there is no such header, the hash of the mailmessage.
    """
    logger.debug("Parsing MessageID ...")
    messageID = mailMessage.get(ParsedMailKeys.Header.MESSAGE_ID)
    if messageID is None:
        logger.warning("No messageID found in mail, resorting to hash!")
        return str(hash(mailMessage))
    else:
        logger.debug("Successfully parsed messageID")
    return messageID


def _parseDate(mailMessage: email.message.Message) -> datetime.datetime:
    """Parses the date header of the given mailmessage.
    Uses :func:`email.utils.parsedate_to_datetime`.
    If none is found uses :attr:`Emailkasten.constants.ParsingConfiguration.DATE_DEFAULT` as a fallback.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        The datetime of the mailmessage.
        If there is no such header, :attr:`Emailkasten.constants.ParsingConfiguration.DATE_DEFAULT`.
    """
    logger.debug("Parsing date ...")
    date = mailMessage.get(ParsedMailKeys.Header.DATE)
    if date is None:
        logger.warning("No DATE found in mail, resorting to default!")
        return datetime.datetime.strptime(ParsingConfiguration.DATE_DEFAULT, ParsingConfiguration.DATE_FORMAT)

    decodedDate = email.utils.parsedate_to_datetime(_decodeHeader(date))
    return decodedDate


def _parseSubject(mailMessage: email.message.Message) -> str:
    """Parses the subject header of the given mailmessage.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        The subject header of the mailmessage.
        If there is no such header, the string is blank.
        If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.
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
    return parsedSubject


def _parseBodyText(mailMessage: email.message.Message) -> str:
    """Parses the bodytext of the given mailmessage.
    Combines all elements of content type text if the message is multipart. Otherwise uses the full message.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        The bodytext of the mailmessage.
        If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.
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
    else:
        parsedBodyText = mailBodyText

    return parsedBodyText


def _parseImages(mailMessage: email.message.Message) -> list[dict]:
    """Parses the inline images in the given mailmessage.
    Looks for elements of content type image that are not an attachment.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        A list of images in the mailmessage.
        Empty if none are found or the message is not multipart.
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

    return images


def _parseAttachments(mailMessage: email.message.Message) -> list[dict[str, Any]]:
    """Parses the attachments in the given mailmessage.
    Looks for elements with content disposition attachment or content type in :attr:`Emailkasten.ParsingConfiguration.APPLICATION_TYPES`.
    If no filename is found for a file uses the hash +.attachment.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        A list of attachments in the mailmessage.
        Empty if none are found or the message is not multipart.
    """
    logger.debug("Parsing attachments ...")
    attachments = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition() == "attachment" or part.get_content_type() in ParsingConfiguration.APPLICATION_TYPES:
                attachmentDict: dict[str,Any] = {}
                attachmentDict[ParsedMailKeys.Attachment.DATA] = part
                attachmentDict[ParsedMailKeys.Attachment.SIZE] = len(part.as_bytes())
                attachmentDict[ParsedMailKeys.Attachment.FILE_NAME] = part.get_filename() or f"{hash(part)}.attachment"
                attachmentDict[ParsedMailKeys.Attachment.FILE_PATH] = None

                attachments.append(attachmentDict)

    if not attachments:
        logger.debug("No attachments found in mail")
    else:
        logger.debug("Successfully parsed attachments")

    return attachments



def _parseHeader(mailMessage: email.message.Message, headerKey: str) -> str:
    """Parses the given header of the given mailmessage.
    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.

    Args:
        mailMessage: The mailmessage to be parsed.
        headerKey: The header to extract from the message.

    Returns:
        The parsed header of the mailmessage.
        Empty if there is no such header.
    """
    logger.debug("Parsing %s ...", headerKey)
    header = mailMessage.get(headerKey, "")
    if header is None:
        logger.debug("No %s found in mail.", headerKey)
    else:
        logger.debug("Successfully parsed %s", headerKey)
    return header



def _parseMultipleHeader(mailMessage: email.message.Message, headerKey: str) -> str|None:
    """Parses the given header, which may appear multiple times, of the given mailmessage.

    Args:
        mailMessage: The mailmessage to be parsed.
        headerKey: The header to extract from the message.

    Returns:
        The combined header from all occurances.
    """
    logger.debug("Parsing %s ...", headerKey)
    headers = mailMessage.get_all(headerKey)
    if headers :
        combinedHeaders = ""
        for item in headers:
            combinedHeaders += item + '\n'
        logger.debug("Successfully parsed %s", headerKey)
        return combinedHeaders
    else:
        logger.debug("No %s found in mail.", headerKey)
        return None



def _parseMailinglist(mailMessage: email.message.Message) -> dict[str, Any]:
    """Parses the mailinglist headers of the given mailmessage.

    Args:
        mailMessage: The mailmessage to be parsed.

    Returns:
        The parsed mailinglist headers in the mailmessage.
    """
    mailinglist = {}
    mailinglist[ParsedMailKeys.MailingList.ID] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.ID)
    mailinglist[ParsedMailKeys.MailingList.OWNER] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.OWNER)
    mailinglist[ParsedMailKeys.MailingList.SUBSCRIBE] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.SUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.UNSUBSCRIBE] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.UNSUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.POST] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.POST)
    mailinglist[ParsedMailKeys.MailingList.HELP] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.HELP)
    mailinglist[ParsedMailKeys.MailingList.ARCHIVE] = _parseHeader(mailMessage, ParsedMailKeys.MailingList.ARCHIVE)
    return mailinglist


def _parseCorrespondents(mailMessage: email.message.Message, mentionHeaderKey: str) -> list[tuple[str,str]]:
    """Parses the correspondents that are mentioned in a given way.

    Args:
        mailMessage: The mailmessage to be parsed.
        mentionHeaderKey: The way the correspondents are mentioned.

    Returns:
        A list of correspondent mailaddresses and mailernames
    """
    logger.debug("Parsing %s ...", mentionHeaderKey)
    correspondents = mailMessage.get_all(mentionHeaderKey)
    if correspondents is None:
        logger.debug("No %s correspondents found in mail!", mentionHeaderKey)
        return []
    else:
        logger.debug("Successfully parsed %s correspondents.", mentionHeaderKey)

    return _separateRFC2822MailAddressFormat(correspondents)



def parseMail(mailToParse: bytes) -> dict[str, Any]:
    """Parses a mail returned by a mail server for its features.
    Uses the various private functions in :mod:`Emailkasten.mailParsing`.

    Args:
        mailToParse: The mail data as supplied by the mailhost.

    Returns:
        The features of the mail in a dictionary with keys as defined in :class:`Emailkasten.constants.ParsedMailKeys`.
    """
    mailMessage = email.message_from_bytes(mailToParse)

    logger.debug("Parsing email with subject %s ...", _parseSubject(mailMessage))

    parsedEMail: dict[str, Any] = {}
    parsedEMail[ParsedMailKeys.DATA] = mailToParse
    parsedEMail[ParsedMailKeys.FULL_MESSAGE] = mailMessage
    parsedEMail[ParsedMailKeys.SIZE] = len(mailToParse)
    parsedEMail[ParsedMailKeys.Header.MESSAGE_ID] = _parseMessageID(mailMessage)
    parsedEMail[ParsedMailKeys.Header.DATE] = _parseDate(mailMessage)
    parsedEMail[ParsedMailKeys.Header.SUBJECT] = _parseSubject(mailMessage)
    parsedEMail[ParsedMailKeys.Header.DATE] = _parseDate(mailMessage)
    parsedEMail[ParsedMailKeys.BODYTEXT] = _parseBodyText(mailMessage)

    for _, correspondentHeader in ParsedMailKeys.Correspondent():
        parsedEMail[correspondentHeader] = _parseCorrespondents(mailMessage, correspondentHeader)

    parsedEMail[ParsedMailKeys.ATTACHMENTS] = _parseAttachments(mailMessage)
    parsedEMail[ParsedMailKeys.IMAGES] = _parseImages(mailMessage)
    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = None
    parsedEMail[ParsedMailKeys.PRERENDER_FILE_PATH] = None

    parsedEMail[ParsedMailKeys.MAILINGLIST] = _parseMailinglist(mailMessage)
    parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO] = _parseHeader(mailMessage, ParsedMailKeys.Header.IN_REPLY_TO)

    parsedEMail[ParsedMailKeys.Header.COMMENTS] = _parseHeader(mailMessage, ParsedMailKeys.Header.COMMENTS)
    parsedEMail[ParsedMailKeys.Header.LANGUAGE] = _parseHeader(mailMessage, ParsedMailKeys.Header.LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_LANGUAGE] = _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_TYPE] = _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_TYPE)

    parsedEMail[ParsedMailKeys.Header.KEYWORDS] = _parseHeader(mailMessage, ParsedMailKeys.Header.KEYWORDS)
    parsedEMail[ParsedMailKeys.Header.RECEIVED] = _parseMultipleHeader(mailMessage, ParsedMailKeys.Header.RECEIVED)
    parsedEMail[ParsedMailKeys.Header.IMPORTANCE] = _parseHeader(mailMessage, ParsedMailKeys.Header.IMPORTANCE)
    parsedEMail[ParsedMailKeys.Header.PRIORITY] = _parseHeader(mailMessage, ParsedMailKeys.Header.PRIORITY)
    parsedEMail[ParsedMailKeys.Header.PRECEDENCE] = _parseHeader(mailMessage, ParsedMailKeys.Header.PRECEDENCE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_LOCATION] = _parseHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LOCATION)
    parsedEMail[ParsedMailKeys.Header.ARCHIVED_AT] = _parseHeader(mailMessage, ParsedMailKeys.Header.ARCHIVED_AT)
    parsedEMail[ParsedMailKeys.Header.USER_AGENT] = _parseHeader(mailMessage, ParsedMailKeys.Header.USER_AGENT)
    parsedEMail[ParsedMailKeys.Header.X_PRIORITY] = _parseHeader(mailMessage, ParsedMailKeys.Header.X_PRIORITY)
    parsedEMail[ParsedMailKeys.Header.X_ORIGINATING_CLIENT] = _parseHeader(mailMessage, ParsedMailKeys.Header.X_ORIGINATING_CLIENT)
    parsedEMail[ParsedMailKeys.Header.X_SPAM_FLAG] = _parseHeader(mailMessage, ParsedMailKeys.Header.X_SPAM_FLAG)
    parsedEMail[ParsedMailKeys.Header.AUTO_SUBMITTED] = _parseHeader(mailMessage, ParsedMailKeys.Header.AUTO_SUBMITTED)

    logger.debug("Successfully parsed mail")
    return parsedEMail


def parseMailbox(mailboxBytes: bytes) -> str:
    """Parses the mailbox name as received by the scanMailboxes method in :mod:`Emailkasten.Fetchers`.

    Args:
        mailboxBytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The name of the mailbox independent of its parent folders
    """
    mailbox = mailboxBytes.decode(ParsingConfiguration.CHARSET_DEFAULT)
    mailboxName = mailbox.split("\"/\"")[1].strip()
    if mailboxName == "":
        mailboxName = mailbox.split("\" \"")[1].strip()
    return mailboxName
