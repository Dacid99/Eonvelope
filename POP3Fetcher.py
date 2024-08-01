import poplib
import os

from MailParser import MailParser

class POP3Fetcher(poplib.POP3): 

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        super().__init__(host, port, timeout)
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
    def fetchAndPrintAll(self):
        messageNumber = len(self.list()[1])
        for number in range(messageNumber):
            messageData = self.retr(number + 1)[1]
            
            fullMessage = b'\n'.join(messageData)
            mailParser = MailParser(fullMessage)
            print(mailParser.parseFrom())
            print(mailParser.parseTo())
            print(mailParser.parseSubject())
            print(mailParser.parseBody())
            print(mailParser.parseDate())
            print(mailParser.parseCc())
            print(mailParser.parseBcc())


