# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`IMAPFetcher` class."""

from __future__ import annotations

import datetime
import imaplib
import logging
from typing import TYPE_CHECKING, Literal

from django.utils import timezone

from core import constants
from core.constants import TestStatusCodes

if TYPE_CHECKING:
    from types import TracebackType

    from core.models.AccountModel import AccountModel
    from core.models.MailboxModel import MailboxModel


class IMAPFetcher:
    """Maintains a connection to the IMAP server and fetches data using :mod:`imaplib`.

    Opens a connection to the IMAP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an IMAP host.

    Attributes:
        account (:class:`core.models.AccountModel`): The model of the account to be fetched from.
        logger (:class:`logging.Logger`): The logger for this instance.
        _mailhost (:class:`imaplib.IMAP4`): The IMAP host this instance connects to.
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


    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the IMAP connection and logs into the account.
        If the connection or session could not be established and the `account` is marked as unhealthy.
        If the connection succeeds, the account is flagged as healthy.

        Args:
            account: The model of the account to be fetched from.
        """
        self.account = account

        self.logger = logging.getLogger(__name__)

        try:
            self.connectToHost()
            self.login()

            self.account.is_healthy = True
            self.account.save(update_fields=['is_healthy'])
            self.logger.debug("Marked %s as healthy", str(self.account))
        except imaplib.IMAP4.error:
            self.logger.error("An IMAP error occured connecting and logging in to %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save(update_fields=['is_healthy'])
            self.logger.info("Marked %s as unhealthy", str(self.account))
        except Exception:
            self.logger.error("An unexpected error occured connecting and logging in to %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save(update_fields=['is_healthy'])
            self.logger.info("Marked %s as unhealthy", str(self.account))


    def connectToHost(self) -> None:
        """Opens the connection to the IMAP server using the credentials from :attr:`account`.
        """
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host}
        if (port := self.account.mail_host_port):
            kwargs["port"] = port
        if (timeout := self.account.timeout):
            kwargs["timeout"] = timeout

        self._mailhost = imaplib.IMAP4(**kwargs)
        self.logger.debug("Successfully connected to %s.", str(self.account))


    def login(self) -> None:
        """Logs into the target account using credentials from :attr:`account`.
        """
        self.logger.debug("Logging into %s ...", str(self.account))
        self._mailhost.login(self.account.mail_address, self.account.password)
        self.logger.debug("Successfully logged into %s.", str(self.account))


    def close(self) -> None:
        """Logs out of the account and closes the connection to the IMAP server if it is open.
        Errors do not flag the account as unhealthy.
        """
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailhost:
            try:
                status, _ = self._mailhost.logout()
                if status == "BYE":
                    self.logger.info("Gracefully closed connection to %s.", str(self.account))
                else:
                    self.logger.warning("Closed connection to %s with response %s.", str(self.account), status)

            except imaplib.IMAP4.error:
                self.logger.error("An IMAP error occured closing connection to %s!", str(self.account), exc_info=True)
            except Exception:
                self.logger.error("An unexpected error occured closing connection to %s!", str(self.account), exc_info=True)
        else:
            self.logger.debug("Connection to %s was already closed.", str(self.account))


    def test(self, mailbox: MailboxModel|None = None ) -> int:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether it can be opened and listed.
        Sets the :attr:`core.models.MailboxModel.is_healthy` flag accordingly.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        self.logger.debug("Testing %s ...", str(self.account))

        try:
            status, responseNoop = self._mailhost.noop()

            if status != "OK":
                errorMessage = responseNoop[0].decode('utf-8') if responseNoop and responseNoop[0] else "Unknown error"
                self.logger.error("Bad response testing %s:\n %s, %s", str(self.account), status, errorMessage)
                self.account.is_healthy = False
                self.account.save(update_fields=['is_healthy'])
                return TestStatusCodes.BAD_RESPONSE

            self.account.is_healthy = True
            self.account.save(update_fields=['is_healthy'])

            self.logger.debug("Successfully tested %s.", str(self.account))

            if mailbox:
                self.logger.debug("Testing %s ...", str(mailbox))

                if mailbox.account != self.account:
                    self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
                    return TestStatusCodes.UNEXPECTED_ERROR

                status, responseSelect = self._mailhost.select(mailbox.name, readonly=True)
                if status != "OK":
                    errorMessage = responseSelect[0].decode('utf-8') if responseSelect and responseSelect[0] else "Unknown error"
                    self.logger.error("Bad response opening %s:\n %s, %s", str(mailbox), status, errorMessage)
                    mailbox.is_healthy = False
                    mailbox.save(update_fields=['is_healthy'])
                    return TestStatusCodes.BAD_RESPONSE

                status, responseList = self._mailhost.list()
                if status != "OK":
                    errorMessage = responseList[0].decode('utf-8') if responseList and isinstance(responseList[0], bytes) else "Unknown error"
                    self.logger.error("Bad response listing %s:\n %s, %s", str(mailbox), status, errorMessage)
                    mailbox.is_healthy = False
                    mailbox.save(update_fields=['is_healthy'])
                    return TestStatusCodes.BAD_RESPONSE

                status, data = self._mailhost.unselect()
                if status != "OK":
                    errorMessage = data[0].decode('utf-8') if data and data[0] else "Unknown error"
                    self.logger.warning("Bad response unselecting %s:\n %s, %s", mailbox, status, errorMessage)
                    mailbox.is_healthy = False
                    mailbox.save(update_fields=['is_healthy'])
                    return TestStatusCodes.BAD_RESPONSE

                mailbox.is_healthy = True
                mailbox.save(update_fields=['is_healthy'])

                self.logger.debug("Successfully tested %s.", str(mailbox))

            return TestStatusCodes.OK

        except imaplib.IMAP4.abort:
            self.logger.error("Abort error occured during test of %s!", str(self.account), exc_info=True)
            return TestStatusCodes.ABORTED
        except imaplib.IMAP4.error:
            self.logger.error("An IMAP error occured during test of %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save(update_fields=['is_healthy'])
            return TestStatusCodes.ERROR
        except Exception:
            self.logger.error("An unexpected error occured during test of %s!", str(self.account), exc_info=True)
            return TestStatusCodes.UNEXPECTED_ERROR


    @staticmethod
    def testAccount(account: AccountModel) -> int:
        """Static method to test the validity of account data.
        The :attr:`core.models.AccountModel.is_healthy` flag is updated accordingly.

        Args:
            account: Data of the account to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with IMAPFetcher(account) as imapFetcher:
            result = imapFetcher.test()
        return result


    @staticmethod
    def testMailbox(mailbox: MailboxModel) -> int:
        """Static method to test the validity of mailbox data.
        The :attr:`core.models.MailboxModel.is_healthy` flag is updated accordingly.

        Args:
            mailbox: Data of the mailbox to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with IMAPFetcher(mailbox.account) as imapFetcher:
            result = imapFetcher.test(mailbox=mailbox)
        return result


    def makeFetchingCriterion(self, criterionName: str) -> str|None:
        """Returns the formatted criterion for the IMAP request, handles dates in particular.

        Args:
            criterionName: The criterion to prepare for the IMAP request.
                If not in :attr:`AVAILABLE_FETCHING_CRITERIA`, returns None.

        Returns:
            Formatted criterion to be used in IMAP request;
            None if `criterionName` is not in :attr:`AVAILABLE_FETCHING_CRITERIA`.
        """
        if criterionName in IMAPFetcher.AVAILABLE_FETCHING_CRITERIA:
            if criterionName == constants.MailFetchingCriteria.DAILY:
                startTime = timezone.now() - datetime.timedelta(days=1)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName == constants.MailFetchingCriteria.WEEKLY:
                startTime = timezone.now() - datetime.timedelta(weeks=1)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName == constants.MailFetchingCriteria.MONTHLY:
                startTime = timezone.now() - datetime.timedelta(weeks=4)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            elif criterionName == constants.MailFetchingCriteria.ANNUALLY:
                startTime = timezone.now() - datetime.timedelta(weeks=52)
                return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]
            else:
                return criterionName

        else:
            self.logger.error("Fetching by %s is not available via protocol %s!", criterionName, self.PROTOCOL)
            return None



    def fetchBySearch(self, mailbox: MailboxModel, criterion: str = constants.MailFetchingCriteria.RECENT) -> list[bytes]:
        """Fetches and returns maildata from a mailbox based on a given criterion.
        If an :class:`imaplib.IMAP4.error` that is not an :class:`imaplib.IMAP4.abort` occurs the mailbox is flagged as unhealthy.
        If a bad response is received when opening or searching the mailbox, it is flagged as unhealthy as well.
        In case of success the mailbox is flagged as healthy.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].
            criterion: Formatted criterion to filter mails in the IMAP request.
                Defaults to :attr:`Emailkasten.constants.MailFetchingCriteria.RECENT`.
                If an invalid criterion is given, returns [].

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox matching the criterion.
            Empty if no such messages are found, if there is no connection to the server or if an error occured.
        """
        if not self._mailhost:
            self.logger.error("No connection to %s!", str(self.account))
            return []

        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            return []

        searchCriterion = self.makeFetchingCriterion(criterion)
        if not searchCriterion:
            return []

        self.logger.debug("Searching and fetching %s messages in %s of %s ...", searchCriterion, str(mailbox), str(self.account))
        try:
            self.logger.debug("Opening mailbox %s ...", str(mailbox))
            status, data = self._mailhost.select(mailbox.name, readonly=True)
            if status != "OK":
                errorMessage = data[0].decode('utf-8') if data and data[0] else "Unknown error"
                self.logger.error("Bad response opening %s:\n %s, %s", str(mailbox), status, errorMessage)
                mailbox.is_healthy = False
                mailbox.save(update_fields=['is_healthy'])
                return []

            self.logger.debug("Successfully opened mailbox.")

            self.logger.debug("Searching %s messages in %s ...", searchCriterion, str(mailbox))
            status, messageUIDs = self._mailhost.uid('SEARCH', searchCriterion)
            if status != "OK":
                errorMessage = messageUIDs[0].decode('utf-8') if messageUIDs and messageUIDs[0] else "Unknown error"
                self.logger.error("Bad response searching for mails in %s:\n %s, %s", mailbox, status, errorMessage)
                mailbox.is_healthy = False
                mailbox.save(update_fields=['is_healthy'])
                return []

            self.logger.info("Found %s messages with uIDs %s in %s.", searchCriterion, messageUIDs, str(mailbox))

            self.logger.debug("Fetching %s messages in %s ...", searchCriterion, str(mailbox))
            mailDataList = []

            for uID in messageUIDs[0].split():
                status, messageData = self._mailhost.uid('FETCH', uID, '(RFC822)')
                if status != "OK":
                    errorMessage = messageData[0].decode('utf-8') if messageData and messageData[0] else "Unknown error"
                    self.logger.warning("Bad response fetching mail %s from %s:\n %s, %s", uID, mailbox, status, errorMessage)
                    continue

                mailDataList.append(messageData[0][1])

            self.logger.debug("Successfully fetched %s messages from %s.", searchCriterion, str(mailbox))

            self.logger.debug("Closing mailbox %s ...", str(mailbox))

            status, data = self._mailhost.unselect()
            if status != "OK":
                errorMessage = data[0].decode('utf-8') if data and data[0] else "Unknown error"
                self.logger.warning("Bad response unselecting %s:\n %s, %s", mailbox, status, errorMessage)
            else:
                self.logger.debug("Successfully closed mailbox.")

        except imaplib.IMAP4.abort:
            self.logger.error("Abort error occured searching and fetching %s messages in %s!", searchCriterion,  str(mailbox), exc_info=True)
            return []
        except imaplib.IMAP4.error:
            self.logger.error("An IMAP error occured searching and fetching %s messages in %s!", searchCriterion,  str(mailbox), exc_info=True)
            mailbox.is_healthy = False
            mailbox.save(update_fields=['is_healthy'])
            return []
        except Exception:
            self.logger.error("An unexpected error occured searching and fetching %s messages in %s!", searchCriterion,  str(mailbox), exc_info=True)
            return []

        self.logger.debug("Successfully searched and fetched %s messages in %s.", searchCriterion, str(mailbox))

        mailbox.is_healthy = True
        mailbox.save(update_fields=['is_healthy'])

        return mailDataList



    def fetchMailboxes(self) -> list[bytes]:
        """Retrieves and returns the data of the mailboxes in the account.
        If an :class:`imaplib.IMAP4.error` that is not an :class:`imaplib.IMAP4.abort` occurs the account is flagged as unhealthy.
        If a bad response is received when listing the mailboxes, it is flagged as unhealthy as well.
        In case of success the account is flagged as healthy.

        Returns:
            List of data of all mailboxes in the account. Empty if none are found.
        """
        if not self._mailhost:
            self.logger.error("No connection to %s!", str(self.account))
            return []

        self.logger.debug("Fetching mailboxes at %s ...", str(self.account))
        try:
            status, mailboxes = self._mailhost.list()
            if status != "OK":
                errorMessage = mailboxes[0].decode('utf-8') if mailboxes and isinstance(mailboxes[0], bytes) else "Unknown error"
                self.logger.error("Bad response trying to fetch mailboxes:\n %s, %s", status, errorMessage)
                self.account.is_healthy = False
                self.account.save(update_fields=['is_healthy'])
                return []

            mailboxesList = []
            for mailboxBytes in mailboxes:
                if isinstance(mailboxBytes, bytes):
                    mailboxesList.append(mailboxBytes)

            self.logger.debug("Successfully fetched mailboxes in %s.", str(self.account))

        except imaplib.IMAP4.abort:
            self.logger.error("Abort error occured fetching mailboxes in %s!", str(self.account), exc_info=True)
            return []
        except imaplib.IMAP4.error:
            self.logger.error("An IMAP error occured fetching mailboxes in %s!", str(self.account), exc_info=True)
            self.account.is_healthy = False
            self.account.save(update_fields=['is_healthy'])
            return []
        except Exception:
            self.logger.error("An unexpected error occured fetching mailboxes in %s!", str(self.account), exc_info=True)
            return []

        self.account.is_healthy = True
        self.account.save(update_fields=['is_healthy'])
        return mailboxesList



    def __enter__(self) -> IMAPFetcher:
        """Framework method for use of class in 'with' statement, creates an instance.

        Returns:
            The new IMAPFetcher instance.
        """
        self.logger.debug("Entering")
        return self


    def __exit__(self, exc_type: BaseException|None, exc_value: BaseException|None, traceback: TracebackType|None) -> Literal[True]:
        """Framework method for use of class in 'with' statement, closes an instance.

        Args:
            exc_type: The exception type that raised close.
            exc_value: The exception value that raised close.
            traceback: The exception traceback that raised close.

        Returns:
            True, exceptions are consumed.
        """
        self.logger.debug("Exiting")
        self.close()
        if exc_value or exc_type:
            self.logger.error("Unexpected error %s occured!", exc_type, exc_info=exc_value)
        return True
