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

Functions:
    :func:`_decodeText`: Decodes a text encoded as bytes.
    :func:`_decodeHeader`: Decodes an email header field encoded as bytes.
    :func:`_separateRFC2822MailAddressFormat`: Splits the RFC2822 address fiels into the mailer name and the mail address.
    :func:`_parseMessageID`: Parses the messageID of the given mailmessage.
    :func:`_parseDate`: Parses the datetime of the given mailmessage.
    :func:`_parseSubject`:  Parses the subject of the given mailmessage.
    :func:`_parseBodyText`: Parses the bodytext of the given mailmessage.
    :func:`_parseImages`: Parses the inline images in the given mailmessage.
    :func:`_parseAttachments`: Parses the attachments in the given mailmessage.
    :func:`_parseAdditionalHeader`: Parses the given header of the given mailmessage.
    :func:`_parseAdditionalMultipleHeader`: Parses the given header, which may appear multiple times, of the given mailmessage.
    :func:`_parseMailinglist`: Parses the mailinglist headers of the given mailmessage.
    :func:`_parseCorrespondents`: Parses the correspondents that are mentioned in a given way.
    :func:`parseMail`: Parses a mail returned by a mail server for its features.
    :func:`parseMailbox`: Parses the mailbox name as received by the scanMailboxes method in :mod:`Emailkasten.Fetchers`.

Global variables:
    logger (:python::class:`logging.Logger`): The logger for this module.
"""

import datetime
import email
import email.header
import email.utils
import logging

import email_validator

from .constants import ParsedMailKeys, ParsingConfiguration

logger = logging.getLogger(__name__)


def _decodeText(text):
    """Decodes a text encoded as bytes.
    Checks for a specific charset to use. If none is found uses the default :attr:`Emailkasten.constants.ParsingConfiguration.CHARSET_DEFAULT`.

    Args:
        text (bytes): The text in bytes format to decode properly.

    Returns:
        str: The decoded text. 
    """
    charset = text.get_content_charset()
    if charset is None:
        charset = ParsingConfiguration.CHARSET_DEFAULT
    decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

    return decodedText


def _decodeHeader(header):
    """Decodes an email header field encoded as bytes.
    Checks for a specific charset to use. If none is found uses the default :attr:`Emailkasten.constants.MailParsingConfiguration.CHARSET_DEFAULT`.
    Uses the :python::func:`email.header.decode_header` function.

    Args:
        header (bytes): The mail header to decode.

    Returns:
        str: The decoded mail header 
    """
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if charset is None:
            decodedString += fragment.decode(ParsingConfiguration.CHARSET_DEFAULT, errors='replace') if isinstance(fragment, bytes) else fragment
        else:
            decodedString += fragment.decode(charset, errors='replace')

    return decodedString
    

def _separateRFC2822MailAddressFormat(mailers):
    """Splits the RFC2822 address fiels into the mailer name mail address.
    Uses :python::func:`email.utils.getaddresses` to seperate and :python::func:`email_validator.validate_email` to validate. 
    TODO: If no valid mailaddress is found uses the entire address as fallback.

    Args:
        mailers (list(str)): A list of address fields to seperate.

    Returns:
        list((str,str)): A list of mailernames and mailaddresses
    """
    decodedMailers = [_decodeHeader(mailer) for mailer in mailers]
    mailAddresses = email.utils.getaddresses(decodedMailers)
    separatedMailers = []
    for mailName, mailAddress in mailAddresses:
        try:
            email_validator.validate_email(mailAddress, check_deliverability=False)
        except email_validator.EmailNotValidError:
            logger.warning(f"Mailaddress is invalid for {mailName}, {mailAddress}!")

        separatedMailers.append( (mailName, mailAddress) )
    return separatedMailers


def _parseMessageID(mailMessage):
    """Parses the messageID header of the given mailmessage.
    If none is found uses the hash of the mailmessage as a fallback.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        str: The messageID header of the mailmessage.
            If there is no such header, the hash of the mailmessage.
    """
    logger.debug("Parsing MessageID ...")
    messageID = mailMessage.get(ParsedMailKeys.Header.MESSAGE_ID)
    if messageID is None:
        logger.warning("No messageID found in mail, resorting to hash!")
        return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
    else:
        logger.debug("Successfully parsed messageID")
    return messageID


def _parseDate(mailMessage):
    """Parses the date header of the given mailmessage.
    Uses :python::func:`email.utils.parsedate_to_datetime`.
    If none is found uses :attr:`Emailkasten.constants.ParsingConfiguration.DATE_DEFAULT` as a fallback.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        datetime: The datetime of the mailmessage.
            If there is no such header, :attr:`Emailkasten.constants.ParsingConfiguration.DATE_DEFAULT`.
    """
    logger.debug("Parsing date ...")
    date = mailMessage.get(ParsedMailKeys.Header.DATE)
    if date is None:
        logger.warning("No DATE found in mail, resorting to default!")
        return datetime.datetime.strptime(ParsingConfiguration.DATE_DEFAULT, ParsingConfiguration.DATE_FORMAT)

    decodedDate = email.utils.parsedate_to_datetime(_decodeHeader(date))
    return decodedDate


def _parseSubject(mailMessage):
    """Parses the subject header of the given mailmessage.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        str: The subject header of the mailmessage.
            If there is no such header, the string is empty.
            If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.
    """
    logger.debug("Parsing subject ...")
    if (subject := mailMessage.get(ParsedMailKeys.Header.SUBJECT)):
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


def _parseBodyText(mailMessage):
    """Parses the bodytext of the given mailmessage.
    Combines all elements of content type text if the message is multipart. Otherwise uses the full message.
    If :attr:`constants.ParsingConfiguration.STRIP_TEXTS` is True, whitespace is stripped.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        str: The bodytext of the mailmessage.
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


def _parseImages(mailMessage):
    """Parses the inline images in the given mailmessage.
    Looks for elements of content type image that are not an attachment.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        list: A list of images in the mailmessage.
            Empty if none are found or the message is not multipart.
    """
    logger.debug("Parsing images ...")
    images = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition() and part.get_content_disposition().startswith('attachment'):
                continue 
            if part.get_content_type().startswith('image/'):
                # imageFileName = part.get_filename()
                # if not imageFileName:
                #     imageFileName = 
                imagesDict = {}
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
        

def _parseAttachments(mailMessage):
    """Parses the attachments in the given mailmessage.
    Looks for elements with content disposition attachment or content type in :attr:`Emailkasten.ParsingConfiguration.APPLICATION_TYPES`.
    If no filename is found for a file uses the hash +.attachment.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        list: A list of attachments in the mailmessage.
            Empty if none are found or the message is not multipart.
    """
    logger.debug("Parsing attachments ...")
    attachments = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if ( part.get_content_disposition() and "attachment" in part.get_content_disposition() ) or ( part.get_content_type() and part.get_content_type() in ParsingConfiguration.APPLICATION_TYPES):
                attachmentDict = {}
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



def _parseAdditionalHeader(mailMessage, headerKey):
    """Parses the given header of the given mailmessage.
    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.
        headerKey (str): The header to extract from the message.

    Returns:
        str: The parsed header of the mailmessage.
            Empty if there is no such header.
    """
    logger.debug(f"Parsing {headerKey} ...")
    header = mailMessage.get(headerKey)
    if header is None:
        logger.debug(f"No {headerKey} found in mail.")
    else:
        logger.debug(f"Successfully parsed {headerKey}")
    return header


def _parseAdditionalMultipleHeader(mailMessage, headerKey):
    """Parses the given header, which may appear multiple times, of the given mailmessage.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.
        headerKey (str): The header to extract from the message.

    Returns:
        list: A list of the parsed headers in the mailmessage.
            Empty if there is no such header.
    """
    logger.debug(f"Parsing {headerKey} ...")
    header = mailMessage.get_all(headerKey)
    if header is None:
        logger.debug(f"No {headerKey} found in mail.")
        return None        
    else:
        allHeaders = ""
        for item in header:
            allHeaders += item + '\n'
        logger.debug(f"Successfully parsed {headerKey}")
        return allHeaders
        


def _parseMailinglist(mailMessage):
    """Parses the mailinglist headers of the given mailmessage.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.

    Returns:
        dict: The parsed mailinglist headers in the mailmessage.
    """
    mailinglist = {}
    mailinglist[ParsedMailKeys.MailingList.ID] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.ID)
    mailinglist[ParsedMailKeys.MailingList.OWNER] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.OWNER)
    mailinglist[ParsedMailKeys.MailingList.SUBSCRIBE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.SUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.UNSUBSCRIBE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.UNSUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.POST] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.POST)
    mailinglist[ParsedMailKeys.MailingList.HELP] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.HELP)
    mailinglist[ParsedMailKeys.MailingList.ARCHIVE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.ARCHIVE)
    return mailinglist


def _parseCorrespondents(mailMessage, mentionHeaderKey):
    """Parses the correspondents that are mentioned in a given way.

    Args:
        mailMessage (:python::class:`email.message.EmailMessage`): The mailmessage to be parsed.
        mentionHeaderKey (str): The way the correspondents are mentioned.

    Returns:
        list((str,str)): A list of correspondent mailaddresses and mailernames
    """
    logger.debug(f"Parsing {mentionHeaderKey} ...")
    correspondents = mailMessage.get_all(mentionHeaderKey)
    if correspondents is None:
        logger.debug(f"No {mentionHeaderKey} correspondents found in mail!")
        return []
    else:
        logger.debug(f"Successfully parsed {mentionHeaderKey} correspondents.")
        
    return _separateRFC2822MailAddressFormat(correspondents)



def parseMail(mailToParse):
    """Parses a mail returned by a mail server for its features.
    Uses the various private functions in :mod:`Emailkasten.mailParsing`.

    Args:
        mailToParse (bytes): The mail data as supplied by the mailhost.

    Returns:
        dict: The features of the mail in a dictionary with keys as defined in :class:`Emailkasten.constants.ParsedMailKeys`.
    """
    mailMessage = email.message_from_bytes(mailToParse)

    logger.debug(f"Parsing email with subject {_parseSubject(mailMessage)} ...")

    parsedEMail = {}
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
    parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.IN_REPLY_TO)
    
    parsedEMail[ParsedMailKeys.Header.COMMENTS] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.COMMENTS)
    parsedEMail[ParsedMailKeys.Header.LANGUAGE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_LANGUAGE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_TYPE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.CONTENT_TYPE)
    
    parsedEMail[ParsedMailKeys.Header.KEYWORDS] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.KEYWORDS)
    parsedEMail[ParsedMailKeys.Header.RECEIVED] = _parseAdditionalMultipleHeader(mailMessage, ParsedMailKeys.Header.RECEIVED)
    parsedEMail[ParsedMailKeys.Header.IMPORTANCE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.IMPORTANCE)
    parsedEMail[ParsedMailKeys.Header.PRIORITY] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.PRIORITY)
    parsedEMail[ParsedMailKeys.Header.PRECEDENCE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.PRECEDENCE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_LOCATION] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LOCATION)
    parsedEMail[ParsedMailKeys.Header.ARCHIVED_AT] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.ARCHIVED_AT)
    parsedEMail[ParsedMailKeys.Header.USER_AGENT] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.USER_AGENT)
    parsedEMail[ParsedMailKeys.Header.X_PRIORITY] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.X_PRIORITY)
    parsedEMail[ParsedMailKeys.Header.X_ORIGINATING_CLIENT] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.X_ORIGINATING_CLIENT)
    parsedEMail[ParsedMailKeys.Header.X_SPAM_FLAG] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.X_SPAM_FLAG)
    parsedEMail[ParsedMailKeys.Header.AUTO_SUBMITTED] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.AUTO_SUBMITTED)
    
    logger.debug("Successfully parsed mail")
    return parsedEMail


def parseMailbox(mailboxBytes):
    """Parses the mailbox name as received by the scanMailboxes method in :mod:`Emailkasten.Fetchers`.
    Decodes using :func:`_decodeText`.

    Args:
        mailboxBytes (bytes): The mailbox name in bytes as received from the mail server.
    
    Returns: 
        str: The name of the mailbox independent of its parent folders
    """
    mailbox = _decodeText(mailboxBytes)
    mailboxName = mailbox.split("\"/\"")[1].strip()
    if mailboxName == "":
        mailboxName = mailbox.split("\" \"")[1].strip()
    return mailboxName