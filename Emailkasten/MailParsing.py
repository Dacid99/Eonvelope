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
import sys
import datetime
import logging
from .constants import ParsingConfiguration 
from .constants import ParsedMailKeys


logger = logging.getLogger(__name__)


#Defaults
__DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
__DATE_DEFAULT = "1971-01-01 00:00:00"  #must fit dateFormat

   
def parseMailbox(mailboxBytes):
    mailbox = mailboxBytes.decode(ParsingConfiguration.CHARSET_DEFAULT)
    mailboxName = mailbox.split("\"/\"")[1].strip()
    if mailboxName == "":
        mailboxName = mailbox.split("\" \"")[1].strip()
    return mailboxName


def _decodeText(text):
    charset = text.get_content_charset()
    if charset is None:
        charset = ParsingConfiguration.CHARSET_DEFAULT
    decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

    return decodedText


def _decodeHeader(header):
        decodedFragments = email.header.decode_header(header)
        decodedString = ""
        for fragment, charset in decodedFragments:
            if charset is None:
                decodedString += fragment.decode(ParsingConfiguration.CHARSET_DEFAULT, errors='replace') if isinstance(fragment, bytes) else fragment
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
        logger.debug(f"Successfully parsed messageID")
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
        decodedSubject = _decodeHeader(subject)
        if ParsingConfiguration.STRIP_TEXTS:
            parsedSubject = decodedSubject.strip()
        else:
            parsedSubject = decodedSubject
        logger.debug(f"Successfully parsed subject")
    else: 
        logger.warning("No SUBJECT found in mail!")
        parsedSubject = ""
    return parsedSubject


def _parseBodyText(mailMessage):
    logger.debug("Parsing bodytext ...")
    mailBodyText = ""
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition():
                continue
            if part.get_content_type() in ['text/plain', 'text/html']:
                mailBodyText += _decodeText(part)
    else:
        mailBodyText = _decodeText(mailMessage)
    if mailBodyText == "":
        logger.warning("No BODYTEXT found in mail!")
    else:
        logger.debug(f"Successfully parsed bodytext")

    if ParsingConfiguration.STRIP_TEXTS:
        parsedBodyText = mailBodyText.strip()
    else:
        parsedBodyText = mailBodyText

    return parsedBodyText


def _parseImages(mailMessage):
    logger.debug("Parsing images ...")
    images = []
    if mailMessage.is_multipart():
        for part in mailMessage.walk():
            if part.get_content_disposition().startswith('attachment'):
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
        logger.debug(f"Successfully parsed images")

    return images
        

def _parseAttachments(mailMessage):
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
        logger.debug(f"Successfully parsed attachments")

    return attachments



def _parseAdditionalHeader(mailMessage, headerKey):
    logger.debug(f"Parsing {headerKey} ...")
    header = mailMessage.get(headerKey)
    if header is None:
        logger.debug(f"No {headerKey} found in mail.")
    else:
        logger.debug(f"Successfully parsed {headerKey}")
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
        


def _parseMailinglist(mailMessage):
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
    logger.debug(f"Parsing {mentionHeaderKey} ...")
    recipients = mailMessage.get_all(mentionHeaderKey)
    if recipients is None:
        logger.info(f"No {mentionHeaderKey} correspondents found in mail!")
        return []
    else:
        logger.debug(f"Successfully parsed {mentionHeaderKey} correspondents.")
    decodedAndSeparatedRecipients = [ _separateRFC2822MailAddressFormat(_decodeHeader(recipient)) for recipient in recipients ]
    return decodedAndSeparatedRecipients



def parseMail(mailToParse):

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
    
    for mentionType, correspondentHeader in ParsedMailKeys.Correspondent():
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
