import poplib
import logging

from MailParser import MailParser

class POP3Fetcher: 

    protocol = "POP3"

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self._mailhost = poplib.POP3(host, port, timeout)
        self.username = username
        self.password = password
        self.login()


    def login(self):
        logging.debug(f"Logging in to {self.host} on port {self.port} with username {self.username} and password {self.password} via {self.protocol} ...")
        try:
            self._mailhost.user(self.username)
            self._mailhost.pass_(self.password)
            logging.debug(f"Successfully logged in to {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
        except poplib.error_proto as e:
            logging.error(f"Failed connecting via {self.protocol} to {self.host} on port {self.port} with username {self.username} and password {self.password}!", exc_info=True)

    def close(self):
        logging.debug(f"Closing connection to {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        if self._mailhost:
            try:
                self._mailhost.quit()
                logging.debug(f"Gracefully closed connection to {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            except imaplib.IMAP4.error:
                logging.error(f"Failed to close connection to {self.host} on port {self.port} with username {self.username} via {self.protocol}!", exc_info=True)

    def fetchAll(self):
        logging.debug(f"Fetching all messages at {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        try:
            messageCount = len(self._mailhost.list()[1])
            logging.debug(f"Found {messageCount} messages at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            parsedMails = []
            for number in range(messageCount):
                messageData = self._mailhost.retr(number + 1)[1]
                fullMessage = b'\n'.join(messageData)
                mailParser = MailParser(fullMessage)
                parsedMails.append(mailParser)
            logging.debug(f"Successfully fetched all messages at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            return parsedMails
        except poplib.error_proto as e:
            logging.error(f"Failed to fetch all messages from {self.host} on port {self.port} with username {self.username} via {self.protocol}!", exc_info=True)
            return []

    def __enter__(self):
        logging.debug("POP3Fetcher._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug("POP3Fetcher._exit_")
        self.close()