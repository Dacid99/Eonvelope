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
from .LoggerFactory import LoggerFactory

class MailParser:
    #Keys to the dict
    dataString = "Raw"
    fullMessageString = "Full"
    sizeString = "Size"
    emlFilePathString = "EmlFilePath"
    prerenderFilePathString = "PrerenderFilePath"
    attachmentsString = "Attachments"
    imagesString = "Images"
    mailinglistString = "Mailinglist"
    #Keys to the xml and the dict
    messageIDHeader = "Message-ID"
    inReplyToHeader = "In-Reply-To"
    fromHeader = "From"
    toHeader = "To"
    bccHeader = "Bcc"
    ccHeader = "Cc"
    replyToHeader = "Reply-To"
    returnPathHeader = "Return-Path"
    envelopeToHeader = "Envelope-To"
    deliveredToHeader = "Delivered-To"
    senderHeader = "Sender"
    
    dateHeader = "Date"
    subjectHeader = "Subject"
    commentsHeader = "Comments"
    keywordsHeader = "Keywords"
    
    receivedHeader = "Received"
    importanceHeader = "Importance"
    priorityHeader = "Priority"
    precedenceHeader = "Precedence"
    returnReceiptTo = "Return-Receipt-To"
    dispositionNotificationTo = "Disposition-Notification-To"
    
    languageHeader = "Language"
    contentLanguageHeader = "Content-Language"
    contentLocationHeader = "Content-Location"
    contentTypeHeader = "Content-Type"
    
    userAgentHeader = "User agent"
    autoSubmittedHeader = "Auto-Submitted"
    archivedAtHeader = "Archived-At"
    
    xPriorityHeader = "X-Priority"
    xOriginatingClientHeader = "X-Originating-Client"
    xSpamFlag = "X-Spam-Flag"

    bodyText = "Bodytext"
    #attachment keys
    attachment_dataString = "AttachmentData"
    attachment_sizeString= "AttachmentSize"
    attachment_fileNameString = "AttachmentFileName"
    attachment_filePathString= "AttachmentFilePath" 
    
    #image keys
    images_dataString = "ImageData"
    images_sizeString= "ImageSize"
    images_fileNameString = "ImageFileName"
    images_filePathString= "ImageFilePath" 
    
    #mailinglist keys
    listIDHeader = "List-Id"
    listOwnerHeader = "List-Owner"
    listSubscribeHeader = "List-Subscribe"
    listUnsubscribeHeader = "List-Unsubscribe"
    listPostHeader = "List-Post"
    listHelpHeader = "List-Help"
    listArchiveHeader = "List-Archive"

    #Defaults
    __dateFormat = '%Y-%m-%d %H:%M:%S'
    __dateDefault = "1971-01-01 00:00:00"  #must fit dateFormat

    @staticmethod
    def parseMailbox(mailboxBytes):
        mailbox = mailboxBytes.decode(constants.ParsingConfiguration.CHARSET_DEFAULT)
        mailboxName = mailbox.split("\"/\"")[1].strip()
        if mailboxName == "":
            mailboxName = mailbox.split("\" \"")[1].strip()
        return mailboxName


    @staticmethod
    def parseMail(mailToParse):
        logger = LoggerFactory.getChildLogger(MailParser.__name__)

        mailMessage = email.message_from_bytes(mailToParse)

        def decodeHeader(header):
            decodedFragments = email.header.decode_header(header)
            decodedString = ""
            for fragment, charset in decodedFragments:
                if charset is None:
                    decodedString += fragment.decode(constants.ParsingConfiguration.CHARSET_DEFAULT, errors='replace') if isinstance(fragment, bytes) else fragment
                else:
                    decodedString += fragment.decode(charset, errors='replace')

            return decodedString


        def decodeText(text):
            charset = text.get_content_charset()
            if charset is None:
                charset = constants.ParsingConfiguration.CHARSET_DEFAULT
            decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

            return decodedText
        

        def separateRFC2822MailAddressFormat(mailer):
            mailName, mailAddress = email.utils.parseaddr(mailer)
            try:
                email_validator.validate_email(mailAddress, check_deliverability=False)
            except email_validator.EmailNotValidError:
                logger.warning(f"Separation of mailname and address failed for {mailer}!")
                mailAddress = mailer 
            
            return (mailName, mailAddress)
        

        def parseMessageID():
            logger.debug("Parsing MessageID ...")
            messageID = mailMessage.get(MailParser.messageIDHeader)
            if messageID is None:
                logger.warning(f"No messageID found in mail, resorting to hash!")
                return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
            else:
                logger.debug("Success")
            return messageID
        
        
        def parseInReplyTo():
            logger.debug("Parsing InReplyTo ...")
            inReplyMessageID = mailMessage.get(MailParser.inReplyToHeader)
            if inReplyMessageID is None:
                logger.debug(f"No In-Reply-To found in mail.")
            else:
                logger.debug("Success")
            return inReplyMessageID


        def parseFrom():
            logger.debug("Parsing From ...")
            sender = mailMessage.get(MailParser.fromHeader)
            if sender is None:
                logger.warning(f"No FROM correspondent found in mail!")
                return None
            else:
                logger.debug("Success")
            return separateRFC2822MailAddressFormat(decodeHeader(sender))


        def parseTo():
            logger.debug("Parsing To ...")
            recipients = mailMessage.get_all(MailParser.toHeader)
            if recipients is None:
                logger.warning(f"No TO correspondents found in mail!")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateRFC2822MailAddressFormat(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseBcc():
            logger.debug("Parsing Bcc ...")
            recipients = mailMessage.get_all(MailParser.bccHeader)
            if recipients is None:
                logger.debug("No BCC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateRFC2822MailAddressFormat(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseCc():
            logger.debug("Parsing Cc ...")
            recipients = mailMessage.get_all(MailParser.ccHeader)
            if recipients is None:
                logger.debug("No CC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateRFC2822MailAddressFormat(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients


        def parseDate():
            logger.debug("Parsing date ...")
            date = mailMessage.get(MailParser.dateHeader)
            if date is None:
                logger.warning("No DATE found in mail, resorting to default!")
                return datetime.datetime.strptime(MailParser.__dateDefault, MailParser.__dateFormat)
     
            decodedDate = email.utils.parsedate_to_datetime(decodeHeader(date))
            return decodedDate
        

        def parseSubject():
            logger.debug("Parsing subject ...")
            if (subject := mailMessage.get(MailParser.subjectHeader)):
                logger.debug("Success")
                decodedSubject = decodeHeader(subject)
                if constants.ParsingConfiguration.STRIP_TEXTS:
                    parsedSubject = decodedSubject.strip()
                else:
                    parsedSubject = decodedSubject
            else: 
                logger.warning("No SUBJECT found in mail!")
                parsedSubject = ""
            return parsedSubject
        

        def parseBody():
            logger.debug("Parsing bodytext ...")
            mailBodyText = ""
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_type() in ['text/plain', 'text/html']:
                        mailBodyText += decodeText(part)
            else:
                mailBodyText = decodeText(mailMessage)
            if mailBodyText == "":
                logger.warning("No BODYTEXT found in mail!")
            else:
                logger.debug("Success")

            if constants.ParsingConfiguration.STRIP_TEXTS:
                parsedBodyText = mailBodyText.strip()
            else:
                parsedBodyText = mailBodyText

            return parsedBodyText
        
        
        def parseAdditionalHeader(headerKey):
            logger.debug(f"Parsing {headerKey} ...")
            header = mailMessage.get(headerKey)
            if header is None:
                logger.debug(f"No {headerKey} found in mail.")
            else:
                logger.debug("Success")
            return header
        
        def parseAdditionalMailAddressHeader(headerKey):
            logger.debug(f"Parsing {headerKey} ...")
            header = mailMessage.get(headerKey)
            if header is None:
                logger.debug(f"No {headerKey} found in mail.")
            else:
                logger.debug("Success")
            return separateRFC2822MailAddressFormat(decodeHeader(headerKey))[1]
        

        def parseImages():
            logger.debug("Parsing images ...")
            images = []
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_type() in ['image/png', 'image/jpeg', 'image/gif']:
                        # imageFileName = part.get_filename()
                        # if not imageFileName:
                        #     imageFileName = 
                        imagesDict = {}
                        imagesDict[MailParser.images_dataString] = part
                        imagesDict[MailParser.images_sizeString] = sys.getsizeof(part)
                        imagesDict[MailParser.images_fileNameString] = part.get_filename()
                        imagesDict[MailParser.images_filePathString] = None 

                        images.append(imagesDict)

            if not images:
                logger.debug("No images found in mail")
            else:
                logger.debug("Success")

            return images
        

        def parseAttachments():
            logger.debug("Parsing attachments ...")
            attachments = []
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_disposition() == "attachment":
                        attachmentDict = {}
                        attachmentDict[MailParser.attachment_dataString] = part
                        attachmentDict[MailParser.attachment_sizeString] = sys.getsizeof(part)
                        attachmentDict[MailParser.attachment_fileNameString] = part.get_filename()
                        attachmentDict[MailParser.attachment_filePathString] = None 

                        attachments.append(attachmentDict)

            if not attachments:
                logger.debug("No attachments found in mail")
            else:
                logger.debug("Success")

            return attachments
        
        
        def parseMailinglist():
            mailinglist = {}
            mailinglist[MailParser.listIDHeader] = parseAdditionalHeader(MailParser.listIDHeader)
            mailinglist[MailParser.listOwnerHeader] = parseAdditionalHeader(MailParser.listOwnerHeader)
            mailinglist[MailParser.listSubscribeHeader] = parseAdditionalMailAddressHeader(MailParser.listSubscribeHeader)
            mailinglist[MailParser.listUnsubscribeHeader] = parseAdditionalMailAddressHeader(MailParser.listUnsubscribeHeader)
            mailinglist[MailParser.listPostHeader] = parseAdditionalHeader(MailParser.listPostHeader)
            mailinglist[MailParser.listHelpHeader] = parseAdditionalHeader(MailParser.listHelpHeader)
            mailinglist[MailParser.listArchiveHeader] = parseAdditionalHeader(MailParser.listArchiveHeader)
            return mailinglist


        logger.debug(f"Parsing email with subject {parseSubject()} ...")


        parsedEMail = {}
        parsedEMail[MailParser.dataString] = mailToParse
        parsedEMail[MailParser.fullMessageString] = mailMessage
        parsedEMail[MailParser.sizeString] = sys.getsizeof(mailToParse)
        parsedEMail[MailParser.messageIDHeader] = parseMessageID()
        parsedEMail[MailParser.subjectHeader] = parseSubject()
        parsedEMail[MailParser.bodyText] = parseBody()
        parsedEMail[MailParser.inReplyToHeader] = parseInReplyTo()
        parsedEMail[MailParser.fromHeader] = parseFrom()
        parsedEMail[MailParser.toHeader] = parseTo()
        parsedEMail[MailParser.ccHeader] = parseCc()
        parsedEMail[MailParser.bccHeader] = parseBcc()
        parsedEMail[MailParser.dateHeader] = parseDate()
        parsedEMail[MailParser.attachmentsString] = parseAttachments()
        parsedEMail[MailParser.imagesString] = parseImages()
        parsedEMail[MailParser.emlFilePathString] = None
        parsedEMail[MailParser.prerenderFilePathString] = None
        
        parsedEMail[MailParser.returnPathHeader] = parseAdditionalMailAddressHeader(MailParser.returnPathHeader)
        parsedEMail[MailParser.commentsHeader] = parseAdditionalHeader(MailParser.commentsHeader)
        parsedEMail[MailParser.languageHeader] = parseAdditionalHeader(MailParser.languageHeader)
        parsedEMail[MailParser.contentLanguageHeader] = parseAdditionalHeader(MailParser.contentLanguageHeader)
        parsedEMail[MailParser.contentTypeHeader] = parseAdditionalHeader(MailParser.contentTypeHeader)
        parsedEMail[MailParser.envelopeToHeader] = parseAdditionalHeader(MailParser.envelopeToHeader)
        parsedEMail[MailParser.deliveredToHeader] = parseAdditionalMailAddressHeader(MailParser.deliveredToHeader)
        parsedEMail[MailParser.senderHeader] = parseAdditionalMailAddressHeader(MailParser.senderHeader)
        parsedEMail[MailParser.replyToHeader] = parseAdditionalMailAddressHeader(MailParser.replyToHeader)
        parsedEMail[MailParser.returnReceiptTo] = parseAdditionalMailAddressHeader(MailParser.returnReceiptTo)
        parsedEMail[MailParser.dispositionNotificationTo] = parseAdditionalMailAddressHeader(MailParser.dispositionNotificationTo)
        
        parsedEMail[MailParser.keywordsHeader] = parseAdditionalHeader(MailParser.keywordsHeader)
        parsedEMail[MailParser.receivedHeader] = parseAdditionalHeader(MailParser.receivedHeader)
        parsedEMail[MailParser.importanceHeader] = parseAdditionalHeader(MailParser.importanceHeader)
        parsedEMail[MailParser.priorityHeader] = parseAdditionalHeader(MailParser.priorityHeader)
        parsedEMail[MailParser.precedenceHeader] = parseAdditionalHeader(MailParser.precedenceHeader)
        parsedEMail[MailParser.contentLocationHeader] = parseAdditionalHeader(MailParser.contentLocationHeader)
        parsedEMail[MailParser.archivedAtHeader] = parseAdditionalHeader(MailParser.archivedAtHeader)
        parsedEMail[MailParser.userAgentHeader] = parseAdditionalHeader(MailParser.userAgentHeader)
        parsedEMail[MailParser.xPriorityHeader] = parseAdditionalHeader(MailParser.xPriorityHeader)
        parsedEMail[MailParser.xOriginatingClientHeader] = parseAdditionalHeader(MailParser.xOriginatingClientHeader)
        parsedEMail[MailParser.xSpamFlag] = parseAdditionalHeader(MailParser.xSpamFlag)
        parsedEMail[MailParser.autoSubmittedHeader] = parseAdditionalHeader(MailParser.autoSubmittedHeader)
        
        parsedEMail[MailParser.mailinglistString] = parseMailinglist()


        logger.debug("Successfully parsed mail")
        return parsedEMail
