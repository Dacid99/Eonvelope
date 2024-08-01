import email 
import email.header
import email.utils

class MailParser:
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __subjectString = "Subject"
    __charsetDefault = "utf-8"

    def __init__(self, mailToParse):
        self.mailMessage = email.message_from_bytes(mailToParse)

    def decodeHeader(self, header):
        decodedFragments = email.header.decode_header(header)
        decodedString = ""
        for fragment, charset in decodedFragments:
            if charset is None:
                decodedString += fragment.decode(MailParser.__charsetDefault, errors='replace') if isinstance(fragment, bytes) else fragment
            else:
                decodedString += fragment.decode(charset, errors='replace')
        return decodedString

    def decodeText(self, text):
        charset = text.get_content_charset()
        if charset is None:
            charset = MailParser.__charsetDefault
        decodedText = text.get_payload(decode=True).decode(charset, errors='replace')
        return decodedText
    
    def separateMailNameAndAdress(self, mailer):
        mailName, mailAddress = email.utils.parseaddr(mailer)
        if mailAddress.find("@") == -1:
            mailAddress = mailer
        return (mailName, mailAddress)

    def parseFrom(self):
        sender = self.decodeHeader(self.mailMessage.get(MailParser.__fromString))
        return self.separateMailNameAndAdress(sender)
    
    def parseTo(self):
        recipients = self.mailMessage.get_all(MailParser.__toString)
        if recipients is None:
            return None
        decodedAndSeparatedRecipients = [self.separateMailNameAndAdress(self.decodeHeader(recipient)) for recipient in recipients]
        return decodedAndSeparatedRecipients
    
    def parseBcc(self):
        recipients = self.mailMessage.get_all(MailParser.__bccString)
        if recipients is None:
            return None
        decodedAndSeparatedRecipients = [self.separateMailNameAndAdress(self.decodeHeader(recipient)) for recipient in recipients]
        return decodedAndSeparatedRecipients

    
    def parseCc(self):
        recipients = self.mailMessage.get_all(MailParser.__ccString)
        if recipients is None:
            return None
        decodedAndSeparatedRecipients = [self.separateMailNameAndAdress(self.decodeHeader(recipient)) for recipient in recipients]
        return decodedAndSeparatedRecipients

    def parseDate(self):
        return self.decodeHeader(self.mailMessage.get(MailParser.__dateString))
    
    def parseSubject(self):
        return self.decodeHeader(self.mailMessage.get(MailParser.__subjectString))
    
    def parseBody(self):
        mailBodyText = ""
        for text in self.mailMessage.walk():
            if text.get_content_type() == 'text/plain':
                mailBodyText += self.decodeText(text)
        return mailBodyText