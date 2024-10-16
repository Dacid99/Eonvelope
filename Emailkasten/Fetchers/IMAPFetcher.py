'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import imaplib
import logging
from django.utils import timezone

from .. import constants
from ..mailParsing import parseMailbox


class IMAPFetcher: 
    
    PROTOCOL = constants.MailFetchingProtocols.IMAP
    
    AVAILABLE_FETCHING_CRITERIA = [
        constants.MailFetchingCriteria.ALL,
        constants.MailFetchingCriteria.UNSEEN,
        constants.MailFetchingCriteria.RECENT,
        constants.MailFetchingCriteria.NEW,
        constants.MailFetchingCriteria.OLD,
        constants.MailFetchingCriteria.FLAGGED,
        constants.MailFetchingCriteria.ANSWERED,
        constants.MailFetchingCriteria.DAILY,
        constants.MailFetchingCriteria.WEEKLY,
        constants.MailFetchingCriteria.MONTHLY,
        constants.MailFetchingCriteria.ANNUALLY
    ]


    def __init__(self, account):
        self.account = account

        self.logger = logging.getLogger(__name__)

        try:
            self.connectToHost()
            self.login()
        except imaplib.IMAP4.error as e:
            self.logger.error(f"Failed logging into {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()
            self.logger.info(f"Marked {str(self.account)} as unhealthy")


    def connectToHost(self):
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = imaplib.IMAP4(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug("Successfully connected to mail account.")
        

    def login(self):
        self.logger.debug(f"Logging into {str(self.account)} ...")
        self._mailhost.login(self.account.mail_address, self.account.password)
        self.logger.debug(f"Successfully logged into {str(self.account)}.")
        

    def close(self):
        self.logger.debug(f"Closing connection to {str(self.account)} ...")
        if self._mailhost:
            try:
                status, _ = self._mailhost.logout()
                if status == "BYE":
                    self.logger.info(f"Gracefully closed connection to {str(self.account)}.")
                else:
                    self.logger.warning(f"Closed connection to {str(self.account)} with response {status}.")

            except imaplib.IMAP4.error:
                self.logger.error(f"Failed to close connection to {str(self.account)}!", exc_info=True)


    def __bool__(self):
        self.logger.debug(f"Testing connection to {str(self.account)}")
        status = self._mailhost is not None
        self.logger.debug(f"Tested account with result {status}.")
        return status


    @staticmethod
    def test(account):
        with IMAPFetcher(account) as imapFetcher:
            return bool(imapFetcher)
        

    def makeFetchingCriterion(criterionName):
        if criterionName in IMAPFetcher.AVAILABLE_FETCHING_CRITERIA:
            if criterionName is constants.MailFetchingCriteria.DAILY:
                startTime = timezone.now() - datetime.timedelta(days=1)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName is constants.MailFetchingCriteria.WEEKLY:
                startTime = timezone.now() - datetime.timedelta(weeks=1)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName is constants.MailFetchingCriteria.MONTHLY:
                startTime = timezone.now() - datetime.timedelta(weeks=4)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName is constants.MailFetchingCriteria.ANNUALLY:
                startTime = timezone.now() - datetime.timedelta(weeks=52)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            else:
                return criterionName

        else:
            self.logger.error(f"Fetching by {criterionName} is not available via protocol {self.PROTOCOL}!")
            return None
            
        
    def fetchBySearch(self, mailbox = 'INBOX', criterionName ='RECENT'):    #for criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        searchCriterion = self.makeFetchingCriterion(criterionName)
        if not searchCriterion:
            return []

        self.logger.debug(f"Searching and fetching {searchCriterion} messages in {mailbox} of {str(self.account)} ...")
        try:
            self.logger.debug(f"Opening mailbox {mailbox} of {str(self.account)} ...")
            self._mailhost.select(mailbox, readonly=True)
            self.logger.debug("Successfully opened mailbox.")
            status, messageNumbers = self._mailhost.uid('SEARCH', None, searchCriterion)
            if status != "OK":
                self.logger.error(f"Bad response searching for mails, response {status}")
                return []
            
            self.logger.info(f"Found {searchCriterion} messages with numbers {messageNumbers} in {mailbox} of {str(self.account)}.")
            
            mailDataList = []
            for number in messageNumbers[0].split():
                status, messageData = self._mailhost.uid('FETCH', number, '(RFC822)')
                if status != "OK":
                    self.logger.error(f"Bad response fetching mail {number}, response {status}")
                    continue

                mailDataList.append(messageData[0][1])
                
            self.logger.debug(f"Finished fetching {searchCriterion} messages from {mailbox} of {str(self.account)}.")

            self.logger.debug(f"Closing mailbox {mailbox} of {str(self.account)} ...")
            self._mailhost.close()
            self.logger.debug("Successfully closed mailbox.")
    
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
                mailboxesList.append(parseMailbox(mailbox))

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

