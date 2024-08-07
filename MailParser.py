import email 
import email.header
import email.utils
import logging
import datetime
import pytz

from LoggerFactory import LoggerFactory
from ParsedEMail import ParsedEMail

class MailParser:
    __messageIDString = "Message-ID"
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __subjectString = "Subject"
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
                logger.warn(f"Separation of mailname and address failed for {mailer}!")
                mailAddress = mailer
            
            return (mailName, mailAddress)
        

        def parseMessageID():
            logger.debug("Parsing MessageID ...")
            messageID = mailMessage.get(MailParser.__messageIDString)
            if messageID is None:
                logger.warn(f"No messageID found in mail, resorting to hash!")
                return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
            else:
                logger.debug("Success")
            return messageID


        def parseFrom():
            logger.debug("Parsing From ...")
            sender = mailMessage.get(MailParser.__fromString)
            if sender is None:
                logger.warn(f"No FROM correspondent found in mail!")
                return None
            else:
                logger.debug("Success")
            return separateMailNameAndAdress(decodeHeader(sender))


        def parseTo():
            logger.debug("Parsing To ...")
            recipients = mailMessage.get_all(MailParser.__toString)
            if recipients is None:
                logger.warn(f"No TO correspondents found in mail!")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseBcc():
            logger.debug("Parsing Bcc ...")
            recipients = mailMessage.get_all(MailParser.__bccString)
            if recipients is None:
                logger.debug("No BCC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        

        def parseCc():
            logger.debug("Parsing Cc ...")
            recipients = mailMessage.get_all(MailParser.__ccString)
            if recipients is None:
                logger.debug("No CC correspondents found in mail")
                return []
            else:
                logger.debug("Success")
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients


        def parseDate():
            logger.debug("Parsing date ...")
            date = mailMessage.get(MailParser.__dateString)
            if date is None:
                logger.warn("No DATE found in mail, resorting to default!")
                return MailParser.__dateDefault
            decodedDate = decodeHeader(date)
            if MailParser.timezone in pytz.all_timezones:
                timezoneObject = pytz.timezone(MailParser.timezone)
            else:
                logger.warn(f"Invalid timezone {MailParser.timezone}, defaulting to UTC!")
                timezoneObject = datetime.timezone.utc
            decodedConvertedDate = email.utils.parsedate_to_datetime(decodedDate).astimezone(timezoneObject).strftime(MailParser.__dateFormat)
            return decodedConvertedDate
        

        def parseSubject():
            logger.debug("Parsing attachments ...")
            if (subject := mailMessage.get(MailParser.__subjectString)):
                logger.debug("Success")
                return decodeHeader(subject)
            else: 
                logger.warn("No SUBJECT found in mail!")
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
                logger.warn("No BODYTEXT found in mail!")
            else:
                logger.debug("Success")

            return mailBodyText


        def parseAttachments():
            logger.debug("Parsing attachments ...")
            attachmentsData = []
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_disposition() == "attachment":
                        attachmentsData.append(part)

            if not attachmentsData:
                logger.debug("No attachments found in mail")
            else:
                logger.debug("Success")


            return attachmentsData


        logger.debug(f"Parsing email with subject {parseSubject()} ...")

        parsedEMail = ParsedEMail()
        parsedEMail.mailMessage = mailMessage
        parsedEMail.messageID = parseMessageID()
        parsedEMail.subject = parseSubject()
        parsedEMail.emailFrom = parseFrom()
        parsedEMail.emailTo = parseTo()
        parsedEMail.emailCc = parseCc()
        parsedEMail.emailBcc = parseBcc()
        parsedEMail.dateReceived = parseDate()
        parsedEMail.bodyText = parseBody()
        parsedEMail.attachmentsData = parseAttachments()

        logger.debug("Successfully parsed mail")
        return parsedEMail