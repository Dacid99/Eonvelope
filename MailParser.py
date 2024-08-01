import email 
import email.header

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
        if charset == None:
            charset = MailParser.__charsetDefault
        decodedText = text.get_payload(decode=True).decode(charset, errors='replace')
        return decodedText
    
    def parseFrom(self):
        return self.decodeHeader(self.mailMessage.get(MailParser.__fromString))
    
    def parseTo(self):
        recipients = self.mailMessage.get_all(MailParser.__toString)
        decodedRecipients = [self.decodeHeader(recipient) for recipient in recipients]
        return decodedRecipients
    
    def parseBcc(self):
        recipients = self.mailMessage.get_all(MailParser.__bccString)
        decodedRecipients = [self.decodeHeader(recipient) for recipient in recipients]
        return decodedRecipients
    
    def parseCc(self):
        recipients = self.mailMessage.get_all(MailParser.__ccString)
        decodedRecipients = [self.decodeHeader(recipient) for recipient in recipients]
        return decodedRecipients

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