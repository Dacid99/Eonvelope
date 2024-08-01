import email 
import email.header

class MailParser:
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __subjectString = "Subject"

    def __init__(self, mailToParse):
        self.mailToParse = mailToParse

    def decodeHeader(self, header):
        decodedFragments = email.header.decode_header(header)
        decodedString = ""
        for fragment, charset in decodedFragments:
            if charset is None:
                decodedString += fragment.decode('utf-8', errors='replace') if isinstance(fragment, bytes) else fragment
            else:
                decodedString += fragment.decode(charset, errors='replace')
        return decodedString

    def decodeText(self, text):
        charset = text.get_content_charset()
        if charset == None:
            charset = 'utf-8'
        decodedText = text.get_payload(decode=True).decode(charset, errors='replace')
        return decodedText
    
    def parseToText(self):
        mailMessage = email.message_from_bytes(self.mailToParse)
        return mailMessage
    
    def parseFrom(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__fromString))
    
    def parseTo(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__toString))
    
    def parseBcc(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__bccString))
    
    def parseCc(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__ccString))

    def parseDate(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__dateString))
    
    def parseSubject(self):
        mailText = self.parseToText()
        return self.decodeHeader(mailText.get(MailParser.__subjectString))
    
    def parseBody(self):
        mailText = self.parseToText()
        mailBodyText = ""
        for text in mailText.walk():
            if text.get_content_type() == 'text/plain':
                mailBodyText += self.decodeText(text)
        return mailBodyText