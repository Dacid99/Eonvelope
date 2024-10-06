'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import email 
import email.header
import email.utils
import email_validator
from . import constants
import sys
import datetime
import logging


logger = logging.getLogger(__name__)


class ParsedMailKeys:
    #Keys to the dict
    DATA = "Raw"
    FULL_MESSAGE = "Full"
    SIZE = "Size"
    EML_FILE_PATH = "EmlFilePath"
    PRERENDER_FILE_PATH = "PrerenderFilePath"
    ATTACHMENTS = "Attachments"
    IMAGES = "Images"
    MAILINGLIST = "Mailinglist"
    BODYTEXT = "Bodytext"
    
    #Keys to the xml and the dict
    class Header:
        MESSAGE_ID = "Message-ID"
        IN_REPLY_TO = "In-Reply-To"
        FROM = "From"
        TO = "To"
        BCC = "Bcc"
        CC = "Cc"
        REPLY_TO = "Reply-To"
        RETURN_PATH = "Return-Path"
        ENVELOPE_TO = "Envelope-To"
        DELIVERED_TO = "Delivered-To"
        SENDER = "Sender"
    
        DATE = "Date"
        SUBJECT = "Subject"
        COMMENTS = "Comments"
        KEYWORDS = "Keywords"
    
        RECEIVED = "Received"
        IMPORTANCE = "Importance"
        PRIORITY = "Priority"
        PRECEDENCE = "Precedence"
        RETURN_RECEIPT_TO = "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO = "Disposition-Notification-To"

        LANGUAGE = "Language"
        CONTENT_LANGUAGE = "Content-Language"
        CONTENT_LOCATION = "Content-Location"
        CONTENT_TYPE = "Content-Type"

        USER_AGENT = "User-Agent"
        AUTO_SUBMITTED = "Auto-Submitted"
        ARCHIVED_AT = "Archived-At"

        X_PRIORITY = "X-Priority"
        X_ORIGINATING_CLIENT = "X-Originating-Client"
        X_SPAM_FLAG = "X-Spam-Flag"

    #attachment keys
    class Attachment:
        DATA = "AttachmentData"
        SIZE= "AttachmentSize"
        FILE_NAME = "AttachmentFileName"
        FILE_PATH= "AttachmentFilePath" 
    
    #image keys
    class Image:
        DATA = "ImageData"
        SIZE= "ImageSize"
        FILE_NAME = "ImageFileName"
        FILE_PATH= "ImageFilePath" 
    
    #mailinglist keys
    class MailingList:
        ID = "List-Id"
        OWNER = "List-Owner"
        SUBSCRIBE = "List-Subscribe"
        UNSUBSCRIBE = "List-Unsubscribe"
        POST = "List-Post"
        HELP = "List-Help"
        ARCHIVE = "List-Archive"

#Defaults
__DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
__DATE_DEFAULT = "1971-01-01 00:00:00"  #must fit dateFormat

   
def parseMailbox(mailboxBytes):
    mailbox = mailboxBytes.decode(constants.ParsingConfiguration.CHARSET_DEFAULT)
    mailboxName = mailbox.split("\"/\"")[1].strip()
    if mailboxName == "":
        mailboxName = mailbox.split("\" \"")[1].strip()
    return mailboxName


def _decodeText(text):
    charset = text.get_content_charset()
    if charset is None:
        charset = constants.ParsingConfiguration.CHARSET_DEFAULT
    decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

    return decodedText


def _decodeHeader(header):
        decodedFragments = email.header.decode_header(header)
        decodedString = ""
        for fragment, charset in decodedFragments:
            if charset is None:
                decodedString += fragment.decode(constants.ParsingConfiguration.CHARSET_DEFAULT, errors='replace') if isinstance(fragment, bytes) else fragment
            else:
                decodedString += fragment.decode(charset, errors='replace')

        return decodedString
    

def _separateRFC2822MailAddressFormat(mailer):
    mailName, mailAddress = email.utils.parseaddr(mailer)
    try:
        email_validator.validate_email(mailAddress, check_deliverability=False)
    except email_validator.EmailNotValidError:
        logger.warning(f"Separation of mailname and address failed for {mailer}!")
        mailAddress = mailer 

    return (mailName, mailAddress)


def _parseMessageID(mailMessage):
    logger.debug("Parsing MessageID ...")
    messageID = mailMessage.get(ParsedMailKeys.Header.MESSAGE_ID)
    if messageID is None:
        logger.warning(f"No messageID found in mail, resorting to hash!")
        return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
    else:
        logger.debug("Success")
    return messageID


def _parseDate(mailMessage):
    logger.debug("Parsing date ...")
    date = mailMessage.get(ParsedMailKeys.Header.DATE)
    if date is None:
        logger.warning("No DATE found in mail, resorting to default!")
        return datetime.datetime.strptime(ParsedMailKeys.__dateDefault, ParsedMailKeys.__dateFormat)

    decodedDate = email.utils.parsedate_to_datetime(_decodeHeader(date))
    return decodedDate


def _parseSubject(mailMessage):
    logger.debug("Parsing subject ...")
    if (subject := mailMessage.get(ParsedMailKeys.Header.SUBJECT)):
        logger.debug("Success")
        decodedSubject = _decodeHeader(subject)
        if constants.ParsingConfiguration.STRIP_TEXTS:
            parsedSubject = decodedSubject.strip()
        else:
            parsedSubject = decodedSubject
    else: 
        logger.warning("No SUBJECT found in mail!")
        parsedSubject = ""
    return parsedSubject


def _parseBody(mailMessage):
    logger.debug("Parsing bodytext ...")
    mailBodyText = ""
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_type() in ['text/plain', 'text/html']:
                mailBodyText += _decodeText(part)
    else:
        mailBodyText = _decodeText(mailMessage)
    if mailBodyText == "":
        logger.warning("No BODYTEXT found in mail!")
    else:
        logger.debug("Success")

    if constants.ParsingConfiguration.STRIP_TEXTS:
        parsedBodyText = mailBodyText.strip()
    else:
        parsedBodyText = mailBodyText

    return parsedBodyText


def _parseImages(mailMessage):
    logger.debug("Parsing images ...")
    images = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_type() in ['image/png', 'image/jpeg', 'image/gif']:
                # imageFileName = part.get_filename()
                # if not imageFileName:
                #     imageFileName = 
                imagesDict = {}
                imagesDict[ParsedMailKeys.Image.DATA] = part
                imagesDict[ParsedMailKeys.Image.SIZE] = sys.getsizeof(part)
                imagesDict[ParsedMailKeys.Image.FILE_NAME] = part.get_filename()
                imagesDict[ParsedMailKeys.Image.FILE_PATH] = None 

                images.append(imagesDict)

    if not images:
        logger.debug("No images found in mail")
    else:
        logger.debug("Success")

    return images
        

def _parseAttachments(mailMessage):
    logger.debug("Parsing attachments ...")
    attachments = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition() == "attachment":
                attachmentDict = {}
                attachmentDict[ParsedMailKeys.Attachment.DATA] = part
                attachmentDict[ParsedMailKeys.Attachment.SIZE] = sys.getsizeof(part)
                attachmentDict[ParsedMailKeys.Attachment.FILE_NAME] = part.get_filename()
                attachmentDict[ParsedMailKeys.Attachment.FILE_PATH] = None 

                attachments.append(attachmentDict)

    if not attachments:
        logger.debug("No attachments found in mail")
    else:
        logger.debug("Success")

    return attachments



def _parseAdditionalHeader(mailMessage, headerKey):
    logger.debug(f"Parsing {headerKey} ...")
    header = mailMessage.get(headerKey)
    if header is None:
        logger.debug(f"No {headerKey} found in mail.")
    else:
        logger.debug("Success")
    return header


def _parseAdditionalMultipleHeader(mailMessage, headerKey):
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
        

def _parseAdditionalMailAddressHeader(mailMessage, headerKey):
    logger.debug(f"Parsing {headerKey} ...")
    header = mailMessage.get(headerKey)
    if header is None:
        logger.debug(f"No {headerKey} found in mail.")
        return header
    else:
        logger.debug("Success")
        return _separateRFC2822MailAddressFormat(_decodeHeader(header))[1]


def _parseMailinglist(mailMessage):
    mailinglist = {}
    mailinglist[ParsedMailKeys.MailingList.ID] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.ID)
    mailinglist[ParsedMailKeys.MailingList.OWNER] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.OWNER)
    mailinglist[ParsedMailKeys.MailingList.SUBSCRIBE] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.MailingList.SUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.UNSUBSCRIBE] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.MailingList.UNSUBSCRIBE)
    mailinglist[ParsedMailKeys.MailingList.POST] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.POST)
    mailinglist[ParsedMailKeys.MailingList.HELP] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.HELP)
    mailinglist[ParsedMailKeys.MailingList.ARCHIVE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.MailingList.ARCHIVE)
    return mailinglist


def _parseMultipleCorrespondents(mailMessage, mentionHeaderKey):
    logger.debug(f"Parsing {mentionHeaderKey} ...")
    recipients = mailMessage.get_all(mentionHeaderKey)
    if recipients is None:
        logger.info(f"No {mentionHeaderKey} correspondents found in mail!")
        return []
    else:
        logger.debug(f"Successfully parsed {mentionHeaderKey} correspondents.")
    decodedAndSeparatedRecipients = [ _separateRFC2822MailAddressFormat(_decodeHeader(recipient)) for recipient in recipients ]
    return decodedAndSeparatedRecipients


def _parseCorrespondent(mailMessage, mentionHeaderKey):
    logger.debug(f"Parsing {mentionHeaderKey} ...")
    sender = mailMessage.get(mentionHeaderKey)
    if sender is None:
        logger.info(f"No {mentionHeaderKey} correspondents found in mail!")
        return None
    else:
        logger.debug(f"Successfully parsed {mentionHeaderKey} correspondents.")
    return _separateRFC2822MailAddressFormat(_decodeHeader(sender))


def parseMail(mailToParse):

    mailMessage = email.message_from_bytes(mailToParse)

    logger.debug(f"Parsing email with subject {_parseSubject()} ...")

    parsedEMail = {}
    parsedEMail[ParsedMailKeys.DATA] = mailToParse
    parsedEMail[ParsedMailKeys.FULL_MESSAGE] = mailMessage
    parsedEMail[ParsedMailKeys.SIZE] = sys.getsizeof(mailToParse)
    parsedEMail[ParsedMailKeys.Header.MESSAGE_ID] = _parseMessageID(mailMessage)
    parsedEMail[ParsedMailKeys.Header.SUBJECT] = _parseSubject(mailMessage)
    parsedEMail[ParsedMailKeys.BODYTEXT] = _parseBody(mailMessage)
    parsedEMail[ParsedMailKeys.Header.IN_REPLY_TO] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.IN_REPLY_TO)
    parsedEMail[ParsedMailKeys.Header.FROM] = _parseCorrespondent(mailMessage, ParsedMailKeys.Header.FROM)
    parsedEMail[ParsedMailKeys.Header.TO] = _parseMultipleCorrespondents(mailMessage, ParsedMailKeys.Header.TO)
    parsedEMail[ParsedMailKeys.Header.CC] = _parseMultipleCorrespondents(mailMessage, ParsedMailKeys.Header.CC)
    parsedEMail[ParsedMailKeys.Header.BCC] = _parseMultipleCorrespondents(mailMessage, ParsedMailKeys.Header.BCC)
    parsedEMail[ParsedMailKeys.Header.DATE] = _parseDate(mailMessage)
    parsedEMail[ParsedMailKeys.ATTACHMENTS] = _parseAttachments(mailMessage)
    parsedEMail[ParsedMailKeys.IMAGES] = _parseImages(mailMessage)
    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = None
    parsedEMail[ParsedMailKeys.PRERENDER_FILE_PATH] = None
    
    parsedEMail[ParsedMailKeys.Header.RETURN_PATH] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.RETURN_PATH)
    parsedEMail[ParsedMailKeys.Header.COMMENTS] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.COMMENTS)
    parsedEMail[ParsedMailKeys.Header.LANGUAGE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_LANGUAGE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.CONTENT_LANGUAGE)
    parsedEMail[ParsedMailKeys.Header.CONTENT_TYPE] = _parseAdditionalHeader(mailMessage, ParsedMailKeys.Header.CONTENT_TYPE)
    parsedEMail[ParsedMailKeys.Header.ENVELOPE_TO] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.ENVELOPE_TO)
    parsedEMail[ParsedMailKeys.Header.DELIVERED_TO] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.DELIVERED_TO)
    parsedEMail[ParsedMailKeys.Header.SENDER] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.SENDER)
    parsedEMail[ParsedMailKeys.Header.REPLY_TO] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.REPLY_TO)
    parsedEMail[ParsedMailKeys.Header.RETURN_RECEIPT_TO] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.RETURN_RECEIPT_TO)
    parsedEMail[ParsedMailKeys.Header.DISPOSITION_NOTIFICATION_TO] = _parseAdditionalMailAddressHeader(mailMessage, ParsedMailKeys.Header.DISPOSITION_NOTIFICATION_TO) 
    
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
    
    parsedEMail[ParsedMailKeys.MAILINGLIST] = _parseMailinglist(mailMessage)


    logger.debug("Successfully parsed mail")
    return parsedEMail
