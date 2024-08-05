

class ParsedEMail:
    def __init__(self):
        self.messageID = None
        self.subject = None
        self.emailFrom = None
        self.emailTo = []
        self.emailCc = []
        self.emailBcc = []
        self.dateReceived = None
        self.bodyText = None

    def hasMessageID():
        return bool(self.messageID)

    def hasSubject(subject):
        return bool(self.subject)

    def hasFrom(subject):
        return bool(self.emailFrom) and True

    def hasTo(subject):
        return bool(self.emailTo) and True

    def hasCc(subject):
        return bool(self.emailCc) and True
    
    def hasBcc(subject):
        return bool(self.emailBcc) and True
    
    def hasDateReceived(subject):
        return bool(self.dateReceived) and True
        
    def hasBodyText(subject):
        return bool(self.bodyText) and True

