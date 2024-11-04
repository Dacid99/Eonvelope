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

import logging
import poplib

from .. import constants


class POP3Fetcher: 
    """Maintains a connection to the POP server and fetches data using :python::mod:`poplib`.

    Opens a connection to the POP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an POP host.

    Attributes:
        account (:class:`Emailkasten.Models.AccountModel`): The model of the account to be fetched from.
        logger (:python::class:`logging.Logger`): The logger for this instance.
        _mailhost (:python::class:`poplib.POP3`): The POP host this instance connects to.
    """

    PROTOCOL = constants.MailFetchingProtocols.POP3
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA = [
        constants.MailFetchingCriteria.ALL
    ]
    """List of all criteria available for fetching. Refers to :class:`constants.MailFetchingCriteria`."""


    def __init__(self, account):
        """Constructor, starts the POP connection and logs into the account.
        If the connection could not be established, `_mailhost` remains None and the `account` is marked as unhealthy.
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
        except poplib.error_proto:
            self.logger.error(f"A POP error occured connecting and logging in to {str(self.account)}!", exc_info=True)
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
        """Opens the connection to the POP server using the credentials from `account`.
        
        Returns:
            None
        """
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = poplib.POP3(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug(f"Successfully connected to {str(self.account)}.")


    def login(self):
        """Logs into the target account using credentials from `account`.
        
        Returns:
            None
        """
        self.logger.debug(f"Logging into {str(self.account)} ...")
        self._mailhost.user(self.account.mail_account)
        self._mailhost.pass_(self.account.password)
        self.logger.debug(f"Successfully logged into {str(self.account)}.")


    def close(self):
        """Logs out of the account and closes the connection to the POP server if it is open.
        
        Returns:
            None
        """
        self.logger.debug(f"Closing connection to {str(self.account)} ...")
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info(f"Successfully closed connection to {str(self.account)}.")
            except poplib.error_proto:
                self.logger.error(f"A POP error occured to closing connection to {str(self.account)}!", exc_info=True)
            except Exception:
                self.logger.error(f"An unexpected error occured closing connection to {str(self.account)}!", exc_info=True)
        else:
            self.logger.debug(f"Connection to {str(self.account)} was already closed.")
        


    def __bool__(self):
        """Returns whether the connection to the POP host is alive.

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
        with POP3Fetcher(account) as pop3Fetcher:
            return bool(pop3Fetcher)


    def fetchAll(self, mailbox):
        """Fetches and returns all maildata from the server.
        If an :python::class:`poplib.POP3.error_proto` occurs the mailbox is flagged as unhealthy.
        If a bad response is received when listing messages, it is flagged as unhealthy as well. 
        In case of success the mailbox is flagged as healthy.
        
        Args:
            mailbox (:class:`Emailkasten.Models.MailboxModel`): Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].

        Returns:
            list: List of :class:`email.message.EmailMessage` mails in the mailbox. Empty if no messages are found or if an error occured.
        """
        if not self._mailhost:
            self.logger.error(f"No connection to {str(self.account)}!")   
            return []
        
        if mailbox.account != self.account:
            self.logger.error(f"{str(mailbox)} is not a mailbox of {self.account}!")
            return []
        
        self.logger.debug(f"Fetching all messages in {str(mailbox)} ...")

        self.logger.debug(f"Listing all messages in {str(mailbox)} ...")
        try:
            status, messageNumbersList, _ = self._mailhost.list()
            if status != b'+OK':
                self.logger.error(f"Bad response listing mails in {str(mailbox)}:\n {status}, {messageNumbersList}!")
                mailbox.is_healthy = False
                mailbox.save()
                return []

            messageCount = len(messageNumbersList)
            self.logger.debug(f"Found {messageCount} messages in {str(mailbox)}.")

            self.logger.debug(f"Retrieving all messages in {str(mailbox)} ...")
            mailDataList = []
        
            for number in range(messageCount):
                status, messageData, _ = self._mailhost.retr(number + 1)
                if status != b'+OK':
                    self.logger.error(f"Bad response retrieving mail {number} in {str(mailbox)}:\n {status}, {messageData}")
                    continue
                    
                fullMessage = b'\n'.join(messageData)
                mailDataList.append(fullMessage)
                
            self.logger.debug(f"Successfully retrieved all messages in {str(mailbox)}.")

        except poplib.error_proto:
            self.logger.error(f"A POP error occured retrieving all messages in {str(mailbox)}!", exc_info=True)
            mailbox.is_healthy = False
            mailbox.save()
            return []
        except Exception:
            self.logger.error(f"An unexpected error occured retrieving all messages in {str(mailbox)}!", exc_info=True)
            return []

        self.logger.debug(f"Successfully fetched all messages in {str(mailbox)}.")
        
        mailbox.is_healthy = True
        mailbox.save()
        
        return mailDataList
    

    def __enter__(self):
        """Framework method for use of class in 'with' statement, creates an instance."""
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """Framework method for use of class in 'with' statement, closes an instance."""
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()
