
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
        self.emlFilePath = None
        self.attachments = []

    def __str__(self):
        return "MessageID: " + self.messageID + "\nSubject: " + self.subject + "\nDate: " + self.dateReceived + "\nFrom: " + str(self.emailFrom) + "\nTo: " + str(self.emailTo) + "\nCc: " + str(self.emailCc) + "\nBcc: " + str(self.emailBcc) + "\nContent: " + self.bodyText

    def hasMessageID(self):
        return bool(self.messageID)

    def hasSubject(self):
        return bool(self.subject)

    def hasFrom(self):
        return bool(self.emailFrom)

    def hasTo(self):
        return bool(self.emailTo)

    def hasCc(self):
        return bool(self.emailCc)
    
    def hasBcc(self):
        return bool(self.emailBcc)
    
    def hasDateReceived(self):
        return bool(self.dateReceived)
        
    def hasBodyText(self):
        return bool(self.bodyText)

    def hasEML(self):
        return bool(self.emlFilePath)

    def hasAttachments(self):
        return bool(self.attachments) 
