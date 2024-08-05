import email 
import email.header
import email.utils
import logging

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

    @staticmethod
    def parse(mailToParse):

        mailMessage = email.message_from_bytes(mailToParse)
        logging.debug(f"Parsing email with content\n{mailMessage}\n ...")

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
                mailAddress = mailer
            return (mailName, mailAddress)
        
        def parseMessageID():
            messageID = mailMessage.get(MailParser.__messageIDString)
            if messageID is None:
                return hash(mailMessage)  #fallback for unique identifier if no messageID found
            return messageID

        def parseFrom():
            sender = mailMessage.get(MailParser.__fromString)
            if sender is None:
                logging.warn("Mail has no From!")
                return None
            return separateMailNameAndAdress(decodeHeader(sender))

        def parseTo():
            recipients = mailMessage.get_all(MailParser.__toString)
            if recipients is None:
                logging.warn("Mail has no To!")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseBcc():
            recipients = mailMessage.get_all(MailParser.__bccString)
            if recipients is None:
                logging.debug("Mail has no Bcc!")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseCc():
            recipients = mailMessage.get_all(MailParser.__ccString)
            if recipients is None:
                logging.debug("Mail has no Cc!")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients

        def parseDate():
            date = mailMessage.get(MailParser.__dateString)
            if date is None:
                logging.warn("Mail has no Date!")
                return MailParser.__dateDefault
            decodedDate = decodeHeader(date)
            decodedConvertedDate = email.utils.parsedate_to_datetime(decodedDate).strftime(MailParser.__dateFormat)
            return decodedConvertedDate
        
        def parseSubject():
            if (subject := mailMessage.get(MailParser.__subjectString)):
                return decodeHeader(subject)
            else: 
                logging.warn("Mail has no Subject!")
                return ""
        
        def parseBody():
            mailBodyText = ""
            if mailMessage.is_multipart():
                for text in mailMessage.walk():
                    if text.get_content_type() in ['text/plain', 'text/html']:
                        mailBodyText += decodeText(text)
                else:
                    mailBodyText = decodeText(mailMessage)
            if not mailBodyText:
                logging.warn("Mail has no Bodytext!")
            return mailBodyText


        
        parsedEMail = ParsedEMail()
        parsedEMail.messageID = parseMessageID()
        parsedEMail.subject = parseSubject()
        parsedEMail.emailFrom = parseFrom()
        parsedEMail.emailTo = parseTo()
        parsedEMail.emailCc = parseCc()
        parsedEMail.emailBcc = parseBcc()
        parsedEMail.dateReceived = parseDate()
        parsedEMail.bodyText = parseBody()

        logging.debug("Success")
        return parsedEMail