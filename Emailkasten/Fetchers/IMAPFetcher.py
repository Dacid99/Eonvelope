# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import imaplib
import logging

from django.utils import timezone

from .. import constants


class IMAPFetcher: 
    """Maintains a connection to the IMAP server and fetches data using :python::mod:`imaplib`.

    Opens a connection to the IMAP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an IMAP host.

    Attributes:
        account (:class:`Emailkasten.Models.AccountModel`): The model of the account to be fetched from.
        logger (:python::class:`logging.Logger`): The logger for this instance.
        _mailhost (:python::class:`imaplib.IMAP4`): The IMAP host this instance connects to.
    """

    PROTOCOL = constants.MailFetchingProtocols.IMAP
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.IMAP`."""
    
    AVAILABLE_FETCHING_CRITERIA = [
        constants.MailFetchingCriteria.ALL,
        constants.MailFetchingCriteria.UNSEEN,
        constants.MailFetchingCriteria.RECENT,
        constants.MailFetchingCriteria.NEW,
        constants.MailFetchingCriteria.OLD,
        constants.MailFetchingCriteria.FLAGGED,
        constants.MailFetchingCriteria.DRAFT,
        constants.MailFetchingCriteria.ANSWERED,
        constants.MailFetchingCriteria.DAILY,
        constants.MailFetchingCriteria.WEEKLY,
        constants.MailFetchingCriteria.MONTHLY,
        constants.MailFetchingCriteria.ANNUALLY
    ]
    """List of all criteria available for fetching. Refers to :class:`constants.MailFetchingCriteria`. For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4."""


    def __init__(self, account):
        """Constructor, starts the IMAP connection and logs into the account.
        If the connection could not be established, `_mailhost` remains None and the `account` is marked as unhealthy.

        Args:
            account (:class:`Emailkasten.Models.AccountModel`): The model of the account to be fetched from.
        
        Returns:
            None
        """
        self.account = account

        self.logger = logging.getLogger(__name__)

        try:
            self.connectToHost()
            self.login()
        except imaplib.IMAP4.error:
            self.logger.error(f"Failed logging into {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()
            self.logger.info(f"Marked {str(self.account)} as unhealthy")


    def connectToHost(self):
        """Opens the connection to the IMAP server using the credentials from `account`.
        
        Returns:
            None
        """
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = imaplib.IMAP4(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug("Successfully connected to mail account.")
        

    def login(self):
        """Logs into the target account using credentials from `account`.
        
        Returns:
            None
        """
        self.logger.debug(f"Logging into {str(self.account)} ...")
        self._mailhost.login(self.account.mail_address, self.account.password)
        self.logger.debug(f"Successfully logged into {str(self.account)}.")
        

    def close(self):
        """Logs out of the account and closes the connection to the IMAP server if it is open.
        
        Returns:
            None
        """
        self.logger.debug(f"Closing connection to {str(self.account)} ...")
        if self._mailhost:
            try:
                status, _ = self._mailhost.logout()
                if status == "BYE":
                    self.logger.info(f"Gracefully closed connection to {str(self.account)}.")
                else:
                    self.logger.warning(f"Closed connection to {str(self.account)} with response {status}.")

            except imaplib.IMAP4.error:
                self.logger.error(f"An IMAP error occured closing connection to {str(self.account)}!", exc_info=True)
            except Exception:
                self.logger.error(f"An unexpected error occured closing connection to {str(self.account)}!", exc_info=True)
        else:
            self.logger.debug(f"Connection to {str(self.account)} was already closed.")
        


    def __bool__(self):
        """Returns whether the connection to the IMAP host is alive.

        Returns:
            bool: Whether `_mailhost` is None or not.
        """
        self.logger.debug(f"Testing connection to {str(self.account)}")
        status = self._mailhost is not None
        self.logger.debug(f"Tested account with result {status}.")
        return status


    @staticmethod
    def test(account):
        """Static method to test the validity of account data.

        Args:
            account (:class:`Emailkasten.Models.AccountModel`): Data of the account to be tested.

        Returns:
            bool: Whether a connection was successfully established or not.
        """
        with IMAPFetcher(account) as imapFetcher:
            return bool(imapFetcher)
        

    def makeFetchingCriterion(self, criterionName):
        """Returns the formatted criterion for the IMAP request, handles dates in particular.

        Args:
            criterionName (str): The criterion to prepare for the IMAP request.
                If not in `AVAILABLE_FETCHING_CRITERIA`, returns None.

        Returns:
            Optional[str]: Formatted criterion to be used in IMAP request;
            None if `criterionName` is not in `AVAILABLE_FETCHING_CRITERIA`.
        """
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
            
        
    def fetchBySearch(self, mailbox = 'INBOX', criterion ='RECENT'):
        """Fetches and returns maildata from a mailbox based on a given criterion.

        Args:
            mailbox (str, optional): Name of the mailbox to fetch data from. Defaults to INBOX.
                If a mailbox that is not in the account is given, returns [].
            criterion (str, optional): Formatted criterion to filter mails in the IMAP request. Defaults to RECENT.
                If an invalid criterion is given, returns []. 

        Returns:
            list: List of :class:`email.Message` mails in the mailbox matching the criterion. Empty if no such messages are found, if there is no connection to the server or if an error occured.
        """
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        searchCriterion = self.makeFetchingCriterion(criterion)
        if not searchCriterion:  
            return []

        self.logger.debug(f"Searching and fetching {searchCriterion} messages in {mailbox} of {str(self.account)} ...")

        self.logger.debug(f"Opening mailbox {mailbox} of {str(self.account)} ...")
        try:
            status, _ = self._mailhost.select(mailbox, readonly=True)
            if status != "OK":
                self.logger.warning(f"Bad response opening mailbox, response {status}!")
            else:
                self.logger.debug("Successfully opened mailbox.")
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured opening mailbox {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured opening mailbox {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        
        self.logger.debug(f"Searching {searchCriterion} messages in {mailbox} of {str(self.account)} ...")
        try:
            status, messageNumbers = self._mailhost.uid('SEARCH', None, searchCriterion)
            if status != "OK":
                self.logger.error(f"Bad response searching for mails, response {status}!")
                return []
            
            self.logger.info(f"Found {searchCriterion} messages with numbers {messageNumbers} in {mailbox} of {str(self.account)}.")
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured searching {searchCriterion} messages in {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured searching {searchCriterion} messages in {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        
        self.logger.debug(f"Fetching {searchCriterion} messages in {mailbox} of {str(self.account)} ...")
        try:
            mailDataList = []
            for number in messageNumbers[0].split():
                status, messageData = self._mailhost.uid('FETCH', number, '(RFC822)')
                if status != "OK":
                    self.logger.error(f"Bad response fetching mail {number}, response {status}!")
                    continue

                mailDataList.append(messageData[0][1])
                
            self.logger.debug(f"Successfully fetched {searchCriterion} messages from {mailbox} of {str(self.account)}.")
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured fetching {searchCriterion} messages in {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured fetching {searchCriterion} messages in {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        
        self.logger.debug(f"Closing mailbox {mailbox} of {str(self.account)} ...")
        try:
            status, _ = self._mailhost.close()
            if status != "OK":
                self.logger.warning(f"Bad response closing {mailbox}!")
            else:
                self.logger.debug("Successfully closed mailbox.")
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured closing mailbox {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured closing mailbox {mailbox} of {str(self.account)}!", exc_info=True)
            return []
        
        self.logger.debug(f"Successfully searched and fetched {searchCriterion} messages in {mailbox} of {str(self.account)}.")
        return mailDataList


    def fetchMailboxes(self):
        """Retrieves and returns the data of the mailboxes in the account.  
        
        Returns:
            list: List of data of all mailboxes in the account. Empty if none are found.
        """
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        self.logger.debug(f"Fetching mailboxes at {str(self.account)} ...")
        try:
            status, mailboxes = self._mailhost.list()
            if status != "OK":
                self.logger.error(f"Bad response trying to fetch mailboxes, response {status}!")                  
                return []
            self.logger.debug(f"Successfully fetched mailboxes in {str(self.account)}.")
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured fetching mailboxes in {str(self.account)}!", exc_info=True)
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured fetching mailboxes in {str(self.account)}!", exc_info=True)
            return []

        return mailboxes



    def __enter__(self):
        """Framework method for use of class in 'with' statement, creates an instance."""
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """Framework method for use of class in 'with' statement, closes an instance."""
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()

