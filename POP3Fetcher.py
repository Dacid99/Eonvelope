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
            self.user(self.__username)
            self.pass_( self.__password)
            method(self, *args, **kwargs)
            self.quit()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.select(mailbox)
        typ, data = self.search(None, 'ALL')
        for number in data[0].split()[-2:]:
            typ, data = self.fetch(number, '(RFC822)')
            print('Message %s\n%s\n' % (number, MailParser.parseTo(data[0][1]))) 


