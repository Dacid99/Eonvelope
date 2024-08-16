import poplib
import os

from ..LoggerFactory import LoggerFactory
from .POP3Fetcher import POP3Fetcher

class POP3_SSL_Fetcher(POP3Fetcher): 

    PROTOCOL = "POP3_SSL"

    def __init__(self, username, password, host: str = "", port: int = 995, ssl_context = None, timeout= None):
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.timeout = timeout
        self._mailhost = poplib.POP3_SSL(host=host, port=port, timeout=timeout, context=ssl_context)
        self.username = username
        self.password = password

        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

        self.login()

        

