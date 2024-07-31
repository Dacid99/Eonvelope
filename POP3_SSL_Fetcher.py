import poplib
import os

from MailParser import MailParser

class POP3Fetcher(poplib.POP3_SSL): 

    def __init__(self, username, password, host: str = "", port: int = 993, keyfile= None, certfile = None, ssl_context = None, timeout= None):
        super().__init__(host, port, keyfile, certfile, timeout, ssl_context)
        self.__username = username
        self.__password = password

    
    def withLogin(method):
        def methodWithLogin(self, *args, **kwargs):
            #maybe with apop or rpop?
            self.user(self.__username)
            self.pass_( self.__password)
            method(self, *args, **kwargs)
            self.quit()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.select(mailbox)
        typ, data = self.search(None, 'ALL')
        messageNumber = len(self.list()[1])
        fullMessage = ""
        for number in range(messageNumber):
            typ, messageData = self.retr(number + 1)
            fullMessage += messageData[1]
        print('Message %s\n%s\n' % (number, MailParser.parseTo(fullMessage))) 


