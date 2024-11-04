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
        If the connection or session could not be established, `_mailhost` remains None and the `account` is marked as unhealthy.
        If the connection succeeds, the account is flagged as healthy.

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
            self.logger.error(f"An IMAP error occured connecting and logging in to {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()
            self.logger.info(f"Marked {str(self.account)} as unhealthy")
        except Exception:
            self.logger.error(f"An unexpected error occured connecting and logging in to {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()
            self.logger.info(f"Marked {str(self.account)} as unhealthy")

        self.account.is_healthy = True
        self.account.save()



    def connectToHost(self):
        """Opens the connection to the IMAP server using the credentials from `account`.
        
        Returns:
            None
        """
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = imaplib.IMAP4(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)      
        self.logger.debug(f"Successfully connected to {str(self.account)}.")
       
        

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
        Errors do not flag the account as unhealty.
        
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
        """Returns whether connecting to the IMAP host is possible.

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
            

        
    def fetchBySearch(self, mailbox, criterion = constants.MailFetchingCriteria.RECENT):
        """Fetches and returns maildata from a mailbox based on a given criterion.
        If an :python::class:`imaplib.IMAP4.error` that is not an :python::class:`imaplib.IMAP4.abort` occurs the mailbox is flagged as unhealthy.
        If a bad response is received when opening or searching the mailbox, it is flagged as unhealthy as well. 
        In case of success the mailbox is flagged as healthy.

        Args:
            mailbox (:class:`Emailkasten.Models.MailboxModel`): Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].
            criterion (str, optional): Formatted criterion to filter mails in the IMAP request. Defaults to :attr:`Emailkasten.constants.MailFetchingCriteria.RECENT`.
                If an invalid criterion is given, returns []. 

        Returns:
            list: List of :class:`email.message.EmailMessage` mails in the mailbox matching the criterion. Empty if no such messages are found, if there is no connection to the server or if an error occured.
        """
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        if mailbox.account != self.account:
            self.logger.error(f"{str(mailbox)} is not a mailbox of {self.account}!")
            return []
        
        searchCriterion = self.makeFetchingCriterion(criterion)
        if not searchCriterion:  
            return []

        self.logger.debug(f"Searching and fetching {searchCriterion} messages in {str(mailbox)} of {str(self.account)} ...")
        try:
            self.logger.debug(f"Opening mailbox {str(mailbox)} ...")
            status, data = self._mailhost.select(mailbox.name, readonly=True)
            if status != "OK":
                errorMessage = data[0].decode('utf-8') if data and data[0] else "Unknown error"
                self.logger.error(f"Bad response opening {str(mailbox)}:\n {status}, {errorMessage}")
                mailbox.is_healthy = False
                mailbox.save()
                return []
            
            self.logger.debug("Successfully opened mailbox.")
        
            self.logger.debug(f"Searching {searchCriterion} messages in {str(mailbox)} ...")
            status, messageUIDs = self._mailhost.uid('SEARCH', None, searchCriterion)
            if status != "OK":
                errorMessage = messageUIDs[0].decode('utf-8') if messageUIDs and messageUIDs[0] else "Unknown error"
                self.logger.error(f"Bad response searching for mails in {mailbox}:\n {status}, {errorMessage}")
                mailbox.is_healthy = False
                mailbox.save()
                return []
            
            self.logger.info(f"Found {searchCriterion} messages with uIDs {messageUIDs} in {str(mailbox)}.")
        
        
            self.logger.debug(f"Fetching {searchCriterion} messages in {str(mailbox)} ...")
            mailDataList = []
        
            for uID in messageUIDs[0].split():
                status, messageData = self._mailhost.uid('FETCH', uID, '(RFC822)')
                if status != "OK":
                    errorMessage = messageData[0].decode('utf-8') if messageData and messageData[0] else "Unknown error"
                    self.logger.warning(f"Bad response fetching mail {uID} from {mailbox}:\n {status}, {errorMessage}")
                    continue

                mailDataList.append(messageData[0][1])
                
            self.logger.debug(f"Successfully fetched {searchCriterion} messages from {mailbox} of {str(self.account)}.")
        
        
            self.logger.debug(f"Closing mailbox {str(mailbox)} ...")
        
            status, data = self._mailhost.close()
            if status != "OK":
                errorMessage = data[0].decode('utf-8') if data and data[0] else "Unknown error"
                self.logger.warning(f"Bad response closing {mailbox}:\n {status}, {errorMessage}")
            else:
                self.logger.debug("Successfully closed mailbox.")

        except imaplib.IMAP4.abort:
            self.logger.error(f"Abort error occured searching and fetching {searchCriterion} messages in {str(mailbox)}!", exc_info=True)
            return []
        except imaplib.IMAP4.error:
            self.logger.error(f"An IMAP error occured searching and fetching {searchCriterion} messages in {str(mailbox)}!", exc_info=True)
            mailbox.is_healthy = False
            mailbox.save()
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured searching and fetching {searchCriterion} messages in {str(mailbox)}!", exc_info=True)
            return []
        
        self.logger.debug(f"Successfully searched and fetched {searchCriterion} messages in {str(mailbox)}.")

        mailbox.is_healthy = True
        mailbox.save()

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
                errorMessage = mailboxes[0].decode('utf-8') if mailboxes and mailboxes[0] else "Unknown error"
                self.logger.error(f"Bad response trying to fetch mailboxes:\n {status}, {errorMessage}")  
                self.account.is_healthy = False
                self.account.save()                
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

