import imaplib
import logging
import email
import email.policy

from LoggerFactory import LoggerFactory
from MailParser import MailParser

class IMAPFetcher: 
    
    protocol = "IMAP"

    def __init__(self, username, password, host: str = "", port: int = 993, timeout= None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._mailhost = imaplib.IMAP4(host, port, timeout)
        self.username = username
        self.password = password

        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

        self.login()
        

    def login(self):
        self.logger.debug(f"Logging in to {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        try:
            self._mailhost.login(self.username, self.password)
            self.logger.info(f"Successfully logged into {self.host} via {self.protocol}.")
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed connecting via {self.protocol} to {self.host} on port {self.port} with username {self.username} and password {self.password}!", exc_info=True)

    def close(self):
        self.logger.debug(f"Closing connection to {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        if self._mailhost:
            try:
                self._mailhost.close()
                self._mailhost.logout()
                self.logger.info(f"Gracefully closed connection to {self.host} on port {self.port} via {self.protocol}.")
            except imaplib.IMAP4.error:
                self.logger.error(f"Failed to close connection to {self.host} on port {self.port} with username {self.username} via {self.protocol}!", exc_info=True)

    def fetchBySearch(self, mailbox = 'INBOX', searchCriterion='RECENT'):    #for criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
        self.logger.debug(f"Searching and fetching {searchCriterion} messages in {mailbox} at {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        try:
            self._mailhost.select(mailbox, readonly=True)
            typ, messageNumbers = self._mailhost.search(None, searchCriterion)
            self.logger.info(f"Found {searchCriterion} messages with numbers {messageNumbers} in {mailbox} at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            parsedMails = []
            for number in messageNumbers[0].split():
                typ, messageData = self._mailhost.fetch(number, '(RFC822)')
                parsedMail = MailParser.parseMail(messageData[0][1]) 
                parsedMails.append(parsedMail)
            self.logger.info(f"Successfully fetched {searchCriterion} messages from {mailbox} at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            return parsedMails
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed to fetch {searchCriterion} messages from {self.host} on port {self.port} with username {self.username} via {self.protocol} !", exc_info=True)
            return []

    def fetchMailboxes(self):
        self.logger.debug(f"Fetching mailboxes at {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        try:
            status, mailboxes = self._mailhost.list()
            mailboxesList = []
            for mailbox in mailboxes:
                mailboxesList.append(MailParser.parseMailbox(mailbox))
            print(mailboxesList)
            self.logger.debug(f"Successfully fetched mailboxes at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            return mailboxesList
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed to fetch mailboxes from {self.host} on port {self.port} with username {self.username} via {self.protocol}!", exc_info=True)
            return []

    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()

