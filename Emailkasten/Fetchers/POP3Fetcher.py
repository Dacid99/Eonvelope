import poplib
import logging

from ..LoggerFactory import LoggerFactory
from ..MailParser import MailParser

class POP3Fetcher: 

    PROTOCOL = "POP3"

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._mailhost = poplib.POP3(host=host, port=port, timeout=timeout)
        self.username = username
        self.password = password

        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

        self.login()


    def login(self):
        self.logger.debug(f"Logging in to {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL} ...")
        try:
            self._mailhost.user(self.username)
            self._mailhost.pass_(self.password)
            self.logger.info(f"Successfully logged in to {self.host} via {self.PROTOCOL}.")
        except poplib.error_proto as e:
            self.logger.error(f"Failed connecting via {self.PROTOCOL} to {self.host} on port {self.port} with username {self.username} and password {self.password}!", exc_info=True)

    def close(self):
        self.logger.debug(f"Closing connection to {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL} ...")
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info(f"Gracefully closed connection to {self.host} on port {self.port} via {self.PROTOCOL}.")
            except imaplib.IMAP4.error:
                self.logger.error(f"Failed to close connection to {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL}!", exc_info=True)

    def fetchAll(self):
        self.logger.debug(f"Fetching all messages at {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL} ...")
        try:
            status, messageNumbersList, _ = self._mailhost.list()
            if status != b'+OK':
                self.logger.error(f"Bad response trying to fetch mails, response {status}")
                return []

            messageCount = len(messageNumbersList)
            self.logger.debug(f"Found {messageCount} messages at {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL}.")
            mailDataList = []
            for number in range(messageCount):
                status, messageData, _ = self._mailhost.retr(number + 1)
                if status != b'+OK':
                    self.logger.error(f"Bad response trying to fetch mail {number}, response {status}")
                    continue
                    
                fullMessage = b'\n'.join(messageData)
                mailDataList.append(fullMessage)

            self.logger.debug(f"Successfully fetched all messages at {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL}.")
            return mailDataList
                
        except poplib.error_proto as e:
            self.logger.error(f"Failed to fetch all messages from {self.host} on port {self.port} with username {self.username} via {self.PROTOCOL}!", exc_info=True)
            return []

    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()
