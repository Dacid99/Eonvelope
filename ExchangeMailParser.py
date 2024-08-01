import exchangelib
import email
import email.header

from MailParser import MailParser

class ExchangeMailParser:

    def __init__(self, mailToParse):
        if isinstance(mailToParse, exchangelib.Message):
            self.mailMessage = mailToParse
        else: raise TypeError('Mail is no in Message format!')

    def parseFrom(self):    
        decodedSender = self.mailMessage.sender
        return (decodedSender.name, decodedSender.email_address)

    def parseTo(self):
        return [(recipient.name, recipient.email_address) for recipient in self.mailMessage.to_recipients]
        
    def parseBcc(self):
        recipients = [(recipient.name, recipient.email_address) for recipient in self.mailMessage.bcc_recipients]
        return recipients
    
    def parseCc(self):
        recipients = [(recipient.name, recipient.email_address) for recipient in self.mailMessage.cc_recipients]
        return recipients
    
    def parseDate(self):
        return str(self.mailMessage.datetime_received)
        
    def parseBody(self):
        return str(self.mailMessage.text_body)
        
    def parseSubject(self):
        return self.decodeHeader(self.mailMessage.subject)
