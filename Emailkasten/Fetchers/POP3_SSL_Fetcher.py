import poplib

from .. import constants
from .POP3Fetcher import POP3Fetcher

class POP3_SSL_Fetcher(POP3Fetcher): 

    PROTOCOL = constants.MailFetchingProtocols.POP3_SSL


    def connectToHost(self):
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = poplib.POP3_SSL(host=self.account.mail_host, port=self.account.mail_host_port, context=None, timeout=None)
        self.logger.debug("Success")

    
    @staticmethod
    def test(account):
        with POP3_SSL_Fetcher(account) as pop3sslFetcher:
            return bool(pop3sslFetcher)

