import imaplib
import logging

from IMAPFetcher import IMAPFetcher

class IMAP_SSL_Fetcher(IMAPFetcher): 

    protocol = "IMAP_SSL"
    
    def __init__(self, username, password, host: str = "", port: int = 993, keyfile= None, certfile = None, ssl_context = None, timeout= None):
        self.host = host
        self.port = port
        self.keyfile = keyfile
        self.certfile = certfile
        self.ssl_context = ssl_context
        self.timeout = timeout
        self._mailhost = imaplib.IMAP4_SSL(host, port, keyfile, certfile, ssl_context, timeout)
        self.username = username
        self.password = password
        self.login()