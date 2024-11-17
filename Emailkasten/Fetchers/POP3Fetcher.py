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

from __future__ import annotations

import logging
import poplib
from typing import TYPE_CHECKING

from .. import constants
from ..constants import TestStatusCodes

if TYPE_CHECKING:
    from ..Models.AccountModel import AccountModel
    from ..Models.MailboxModel import MailboxModel


class POP3Fetcher:
    """Maintains a connection to the POP server and fetches data using :python::mod:`poplib`.

    Opens a connection to the POP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an POP host.

    Attributes:
        account (:class:`Emailkasten.Models.AccountModel`): The model of the account to be fetched from.
        logger (:class:`logging.Logger`): The logger for this instance.
        _mailhost (:python::class:`poplib.POP3`): The POP host this instance connects to.
    """

    PROTOCOL = constants.MailFetchingProtocols.POP3
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA = [
        constants.MailFetchingCriteria.ALL
    ]
    """List of all criteria available for fetching. Refers to :class:`constants.MailFetchingCriteria`."""


    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the POP connection and logs into the account.
        If the connection could not be established, :attr:`_mailhost` remains None and the `account` is marked as unhealthy.
        If the connection succeeds, the account is flagged as healthy.

        Args:
            account: The model of the account to be fetched from.
        """
        self.account = account

        self.logger = logging.getLogger(__name__)

        try:
            self.connectToHost()
            self.login()
        except poplib.error_proto:
            self.logger.error("A POP error occured connecting and logging in to %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save()
            self.logger.info("Marked %s as unhealthy", str(self.account))
            return
        except Exception:
            self.logger.error("An unexpected error occured connecting and logging in to %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save()
            self.logger.info("Marked %s as unhealthy", str(self.account))
            return

        self.account.is_healthy = True
        self.account.save()


    def connectToHost(self) -> None:
        """Opens the connection to the POP server using the credentials from :attr:`account`.
        """
        self.logger.debug("Connecting to %s ...", str(self.account))
        self._mailhost = poplib.POP3(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug("Successfully connected to %s.", str(self.account))


    def login(self) -> None:
        """Logs into the target account using credentials from :attr:`account`.
        """
        self.logger.debug("Logging into %s ...", str(self.account))
        self._mailhost.user(self.account.mail_account)
        self._mailhost.pass_(self.account.password)
        self.logger.debug("Successfully logged into %s.", str(self.account))


    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open.
        """
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info("Successfully closed connection to %s.", str(self.account))
            except poplib.error_proto:
                self.logger.error("A POP error occured to closing connection to %s!", str(self.account), exc_info=True)
            except Exception:
                self.logger.error("An unexpected error occured closing connection to %s!", str(self.account), exc_info=True)
        else:
            self.logger.debug("Connection to %s was already closed.", str(self.account))


    def test(self, mailbox: MailboxModel|None = None) -> int:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether messages can be listed.
        Sets the The :attr:`Emailkasten.Models.MailboxModel.is_healthy` flag accordingly.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        self.logger.debug("Testing %s ...", str(self.account))
        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            return TestStatusCodes.UNEXPECTED_ERROR

        try:
            status, response = self._mailhost.noop()

            if status != b'+OK':
                self.logger.error("Bad response testing %s:\n %s, %s", str(self.account), status, response)
                self.account.is_healthy = False
                self.account.save()

                return TestStatusCodes.BAD_RESPONSE

            self.account.is_healthy = True
            self.account.save()
            self.logger.debug("Successfully tested %s.", str(self.account))

            if mailbox:
                self.logger.debug("Testing %s ...", str(mailbox))

                status, response = self._mailhost.list()

                if status != b'+OK':
                    self.logger.error("Bad response listing %s:\n %s, %s", str(mailbox), status, response)
                    mailbox.is_healthy = False
                    mailbox.save()

                    return TestStatusCodes.BAD_RESPONSE

                mailbox.is_healthy = True
                mailbox.save()
                self.logger.debug("Successfully tested %s ...", str(mailbox))

            return TestStatusCodes.OK

        except poplib.error_proto:
            self.logger.error("An IMAP error occured during test of %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save()
            return TestStatusCodes.ERROR
        except Exception:
            self.logger.error("An unexpected error occured during test of %s!", str(self.account), exc_info=True)
            return TestStatusCodes.UNEXPECTED_ERROR


    @staticmethod
    def testAccount(account: AccountModel) -> int:
        """Static method to test the validity of account data.
        The :attr:`Emailkasten.Models.AccountModel.is_healthy` flag is updated accordingly.

        Args:
            account: Data of the account to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with POP3Fetcher(account) as pop3Fetcher:
            return pop3Fetcher.test()


    @staticmethod
    def testMailbox(mailbox: MailboxModel) -> int:
        """Static method to test the validity of mailbox data.
        The :attr:`Emailkasten.Models.MailboxModel.is_healthy` flag is updated accordingly.

        Args:
            mailbox: Data of the mailbox to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with POP3Fetcher(mailbox.account) as pop3Fetcher:
            return pop3Fetcher.test(mailbox=mailbox)


    def fetchAll(self, mailbox: MailboxModel) -> list[bytes]:
        """Fetches and returns all maildata from the server.
        If an :python::class:`poplib.error_proto` occurs the mailbox is flagged as unhealthy.
        If a bad response is received when listing messages, it is flagged as unhealthy as well.
        In case of success the mailbox is flagged as healthy.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox. Empty if no messages are found or if an error occured.
        """
        if not self._mailhost:
            self.logger.error("No connection to %s!", str(self.account))
            return []

        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            return []

        self.logger.debug("Fetching all messages in %s ...", str(mailbox))

        self.logger.debug("Listing all messages in %s ...", str(mailbox))
        try:
            status, messageNumbersList, _ = self._mailhost.list()
            if status != b'+OK':
                self.logger.error("Bad response listing mails in %s:\n %s, %s!", str(mailbox), status, messageNumbersList)
                mailbox.is_healthy = False
                mailbox.save()
                return []

            messageCount = len(messageNumbersList)
            self.logger.debug("Found %s messages in %s.", messageCount, str(mailbox))

            self.logger.debug("Retrieving all messages in %s ...", str(mailbox))
            mailDataList = []

            for number in range(messageCount):
                status, messageData, _ = self._mailhost.retr(number + 1)
                if status != b'+OK':
                    self.logger.error("Bad response retrieving mail %s in %s:\n %s, %s", number, str(mailbox), status, messageData)
                    continue

                fullMessage = b'\n'.join(messageData)
                mailDataList.append(fullMessage)

            self.logger.debug("Successfully retrieved all messages in %s.", str(mailbox))

        except poplib.error_proto:
            self.logger.error("A POP error occured retrieving all messages in %s!", str(mailbox), exc_info=True)
            mailbox.is_healthy = False
            mailbox.save()
            return []
        except Exception:
            self.logger.error("An unexpected error occured retrieving all messages in %s!", str(mailbox), exc_info=True)
            return []

        self.logger.debug("Successfully fetched all messages in %s.", str(mailbox))

        mailbox.is_healthy = True
        mailbox.save()

        return mailDataList


    def __enter__(self):
        """Framework method for use of class in 'with' statement, creates an instance."""
        self.logger.debug("%s._enter_", str(self.__class__.__name__))
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        """Framework method for use of class in 'with' statement, closes an instance."""
        self.logger.debug("%s._exit_", str(self.__class__.__name__))
        self.close()
