import email 
import email.header
import email.utils
import logging
import sys
import datetime
from .LoggerFactory import LoggerFactory

class MailParser:
    #Keys to the dict
    dataString = "Raw"
    fullMessageString = "Full"
    sizeString = "Size"
    emlFilePathString = "EmlFilePath"
    attachmentsString = "Attachments"
    #Keys to the xml and the dict
    messageIDString = "Message-ID"
    fromString = "From"
    toString = "To"
    bccString = "Bcc"
    ccString = "Cc"
    dateString = "Date"
    subjectString = "Subject"
    bodyTextString = "Bodytext"

    #attachment keys
    attachment_dataString = "AttachmentData"
    attachment_sizeString= "AttachmentSize"
    attachment_fileNameString = "AttachmentFileName"
    attachment_filePathString= "AttachmentFilePath" 

    #Defaults
    __charsetDefault = "utf-8"
    __dateFormat = '%Y-%m-%d %H:%M:%S'
    __dateDefault = "1971-01-01 00:00:00"  #must fit dateFormat
    timezone = "Europe/Berlin"

    @staticmethod
    def parseMailbox(mailboxBytes):
        mailbox = mailboxBytes.decode(MailParser.__charsetDefault)
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
                    decodedString += fragment.decode(MailParser.__charsetDefault, errors='replace') if isinstance(fragment, bytes) else fragment
                else:
                    decodedString += fragment.decode(charset, errors='replace')

            return decodedString


        def decodeText(text):
            charset = text.get_content_charset()
            if charset is None:
                charset = MailParser.__charsetDefault
            decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

            return decodedText
        

        def separateMailNameAndAdress(mailer):
            mailName, mailAddress = email.utils.parseaddr(mailer)
            if mailAddress.find("@") == -1:
                logger.warning(f"Separation of mailname and address failed for {mailer}!")
                mailAddress = mailer
            
            return (mailName, mailAddress)
        

        def parseMessageID():
            logger.debug("Parsing MessageID ...")
            messageID = mailMessage.get(MailParser.messageIDString)
            if messageID is None:
                logger.warning(f"No messageID found in mail, resorting to hash!")
                return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
            else:
                logger.debug("Success")
            return messageID


        def parseFrom():
            logger.debug("Parsing From ...")
            sender = mailMessage.get(MailParser.fromString)
            if sender is None:
                logger.warning(f"No FROM correspondent found in mail!")
                return None
            else:
                logger.debug("Success")
            return separateMailNameAndAdress(decodeHeader(sender))


        def parseTo():
            logger.debug("Parsing To ...")
            recipients = mailMessage.get_all(MailParser.toString)
            if recipients is None:
                logger.warning(f"No TO correspondents found in mail!")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseBcc():
            logger.debug("Parsing Bcc ...")
            recipients = mailMessage.get_all(MailParser.bccString)
            if recipients is None:
                logger.debug("No BCC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseCc():
            logger.debug("Parsing Cc ...")
            recipients = mailMessage.get_all(MailParser.ccString)
            if recipients is None:
                logger.debug("No CC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients


        def parseDate():
            logger.debug("Parsing date ...")
            date = mailMessage.get(MailParser.dateString)
            if date is None:
                logger.warning("No DATE found in mail, resorting to default!")
                return datetime.datetime.strptime(MailParser.__dateDefault, MailParser.__dateFormat)
     
            decodedDate = email.utils.parsedate_to_datetime(decodeHeader(date))
            return decodedDate
        

        def parseSubject():
            logger.debug("Parsing attachments ...")
            if (subject := mailMessage.get(MailParser.subjectString)):
                logger.debug("Success")
                return decodeHeader(subject)
            else: 
                logger.warning("No SUBJECT found in mail!")
                return ""
        

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

            return mailBodyText


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


        logger.debug(f"Parsing email with subject {parseSubject()} ...")


        parsedEMail = {}
        parsedEMail[MailParser.dataString] = mailToParse
        parsedEMail[MailParser.fullMessageString] = mailMessage
        parsedEMail[MailParser.sizeString] = sys.getsizeof(mailToParse)
        parsedEMail[MailParser.messageIDString] = parseMessageID()
        parsedEMail[MailParser.subjectString] = parseSubject()
        parsedEMail[MailParser.bodyTextString] = parseBody()
        parsedEMail[MailParser.fromString] = parseFrom()
        parsedEMail[MailParser.toString] = parseTo()
        parsedEMail[MailParser.ccString] = parseCc()
        parsedEMail[MailParser.bccString] = parseBcc()
        parsedEMail[MailParser.dateString] = parseDate()
        parsedEMail[MailParser.attachmentsString] = parseAttachments()
        parsedEMail[MailParser.emlFilePathString] = None




        logger.debug("Successfully parsed mail")
        return parsedEMail
