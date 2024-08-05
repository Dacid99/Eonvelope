import email 
import email.header
import email.utils

from ParsedEMail import ParsedEMail

class MailParser:
    __messageIDString = "Message-ID"
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __dateFormat = '%Y-%m-%d %H:%M:%S'
    __subjectString = "Subject"
    __charsetDefault = "utf-8"
    __noneDefaultString = ""

    @staticmethod
    def parse(mailToParse):

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
                return None
            return separateMailNameAndAdress(decodeHeader(sender))

        def parseTo():
            recipients = mailMessage.get_all(MailParser.__toString)
            if recipients is None:
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseBcc():
            recipients = mailMessage.get_all(MailParser.__bccString)
            if recipients is None:
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseCc():
            recipients = mailMessage.get_all(MailParser.__ccString)
            if recipients is None:
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients

        def parseDate(self):
            date = mailMessage.get(MailParser.__dateString)
            if date is None:
                return None
            decodedDate = decodeHeader(date)
            decodedConverterDate = email.utils.parsedate_to_datetime(decodedDate).strftime(MailParser.__dateFormat)
            return decodedConverterDate
        
        def parseSubject():
            if (subject := mailMessage.get(MailParser.__subjectString)):
                return decodeHeader(subject)
            else: return None
        
        def parseBody():
            mailBodyText = ""
            for text in mailMessage.walk():
                if text.get_content_type() == 'text/plain':
                    mailBodyText += decodeText(text)
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
        return parsedEMail