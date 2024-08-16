import imaplib

from ..LoggerFactory import LoggerFactory
from .IMAPFetcher import IMAPFetcher

class IMAP_SSL_Fetcher(IMAPFetcher): 

    PROTOCOL = "IMAP_SSL"
    
    def __init__(self, username, password, host: str = "", port: int = 993, ssl_context = None, timeout= None):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.timeout = timeout
        self._mailhost = imaplib.IMAP4_SSL(host=host, port=port, ssl_context=ssl_context, timeout=timeout)
        self.username = username
        self.password = password

        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

        self.login()
