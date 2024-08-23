import imaplib

from .. import constants
from .IMAPFetcher import IMAPFetcher

class IMAP_SSL_Fetcher(IMAPFetcher): 

    PROTOCOL = constants.MailFetchingProtocols.IMAP_SSL

    def connectToHost(self):
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = imaplib.IMAP4_SSL(host=self.account.mail_host, port=self.account.mail_host_port, ssl_context=None, timeout=None)
        self.logger.debug("Success")


    @staticmethod
    def test(account):
        with IMAP_SSL_Fetcher(account) as imapsslFetcher:
            return bool(imapsslFetcher) 