import imaplib

from .. import constants
from ..LoggerFactory import LoggerFactory
from ..MailParser import MailParser

class IMAPFetcher: 
    
    PROTOCOL = constants.MailFetchingProtocols.IMAP

    def __init__(self, account):
        self.account = account

        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)
        try:
            self.connectToHost()
            self.login()
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed logging into {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()

    def connectToHost(self):
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = imaplib.IMAP4(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug("Success")
        

    def login(self):
        self.logger.debug(f"Logging into {str(self.account)} ...")
        self._mailhost.login(self.account.mail_address, self.account.password)
        self.logger.info(f"Successfully logged into {str(self.account)}.")
        

    def close(self):
        self.logger.debug(f"Closing connection to {str(self.account)} ...")
        if self._mailhost:
            try:
                status, _ = self._mailhost.logout()
                if status == "BYE":
                    self.logger.info(f"Gracefully closed connection to {str(self.account)}.")
                else:
                    self.logger.info(f"Closed connection to {str(self.account)} with response {status}.")

            except imaplib.IMAP4.error:
                self.logger.error(f"Failed to close connection to {str(self.account)}!", exc_info=True)

    @staticmethod
    def test(account):
        imapFetcher = IMAPFetcher(account)
        return imapFetcher is not None
        
        

    def fetchBySearch(self, mailbox = 'INBOX', searchCriterion='RECENT'):    #for criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        self.logger.debug(f"Searching and fetching {searchCriterion} messages in {mailbox} of {str(self.account)} ...")
        try:
            self.logger.debug(f"Opening {mailbox} of {str(self.account)} ...")
            self._mailhost.select(mailbox, readonly=True)
            self.logger.debug("Success")
            status, messageNumbers = self._mailhost.search(None, searchCriterion)
            if status != "OK":
                self.logger.error(f"Bad response searching for mails, response {status}")
                return []
            
            self.logger.info(f"Found {searchCriterion} messages with numbers {messageNumbers} in {mailbox} of {str(self.account)}.")
            
            mailDataList = []
            for number in messageNumbers[0].split():
                status, messageData = self._mailhost.fetch(number, '(RFC822)')
                if status != "OK":
                    self.logger.error(f"Bad response fetching mail {number}, response {status}")
                    continue

                mailDataList.append(messageData[0][1])
                
            self.logger.info(f"Finished fetching {searchCriterion} messages from {mailbox} of {str(self.account)}.")
            self.logger.debug(f"Closing {mailbox} of {str(self.account)} ...")
            self._mailhost.close()
            self.logger.debug("Success")
    
            return mailDataList

        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed to fetch {searchCriterion} messages from {str(self.account)}!", exc_info=True)
            return []


    def fetchMailboxes(self):
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        self.logger.debug(f"Fetching mailboxes at {str(self.account)} ...")
        try:
            status, mailboxes = self._mailhost.list()
            if status != "OK":
                self.logger.error(f"Bad response trying to scan mailboxes, response {status}")                  
                return []

            mailboxesList = []
            for mailbox in mailboxes:
                mailboxesList.append(MailParser.parseMailbox(mailbox))

            self.logger.debug(f"Successfully fetched mailboxes in {str(self.account)}.")
            return mailboxesList

        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed to fetch mailboxes in {str(self.account)}!", exc_info=True)
            return []

    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()

