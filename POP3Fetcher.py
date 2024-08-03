import poplib
import os

from MailParser import MailParser

class POP3Fetcher: 

    protocol = "POP3"

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.__mailhost = poplib.POP3(host, port, timeout)
        self.username = username
        self.password = password
        self.login()


    def login(self):
        logging.debug(f"Logging in to {self.host} on port {self.port} with username {self.username} and password {self.password} via {self.protocol} ...")
        try:
            self.__mailhost.user(self.username)
            self.__mailhost.pass_(self.password)
            logging.debug(f"Successfully logged in to {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
        except poplib.error_proto as e:
            logging.error(f"Failed connecting via {self.protocol} to {self.host} on port {self.port} with username {self.username} and password {self.password}!")

    def close(self):
        logging.debug(f"Closing connection to {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        if self.__mailhost:
            try:
                self.__mailhost.quit()
                logging.debug(f"Gracefully closed connection to {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            except imaplib.IMAP4.error:
                logging.error(f"Failed to close connection to {self.host} on port {self.port} with username {self.username} via {self.protocol}!")

    def fetchLatest(self):
        logging.debug(f"Fetching from {mailbox} at {self.host} on port {self.port} with username {self.username} via {self.protocol} ...")
        try:
            messageNumber = len(self.__mailhost.list()[1])
            number=messageNumber-1
            messageData = self.__mailhost.retr(number + 1)[1]
            fullMessage = b'\n'.join(messageData)
            mailParser = MailParser(fullMessage)
            logging.debug(f"Successfully fetched from {mailbox} at {self.host} on port {self.port} with username {self.username} via {self.protocol}.")
            return mailParser
        except poplib.error_proto as e:
            logging.error(f"Failed to fetch data via {self.protocol} from {self.host} on port {self.port} with username {self.username}!")
            return None

    def __enter__(self):
        logging.debug("POP3Fetcher.__enter__")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug("POP3Fetcher.__exit__")
        self.close()