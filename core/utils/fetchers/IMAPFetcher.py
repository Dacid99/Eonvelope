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
from typing import TYPE_CHECKING, Final, override

from django.utils import timezone

from core.utils.fetchers.exceptions import FetcherError, MailAccountError
from core.utils.fetchers.SafeIMAPMixin import SafeIMAPMixin

from ...constants import MailFetchingCriteria, MailFetchingProtocols
from .BaseFetcher import BaseFetcher


if TYPE_CHECKING:
    from ...models.AccountModel import AccountModel
    from ...models.MailboxModel import MailboxModel


class IMAPFetcher(BaseFetcher, SafeIMAPMixin):
    """Maintains a connection to the IMAP server and fetches data using :mod:`imaplib`.

    Opens a connection to the IMAP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an IMAP host.

    Attributes:
        account (:class:`core.models.AccountModel`): The model of the account to be fetched from.
        logger (:class:`logging.Logger`): The logger for this instance.
        _mailClient (:class:`imaplib.IMAP4`): The IMAP host this instance connects to.
    """

    PROTOCOL = MailFetchingProtocols.IMAP
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.IMAP`."""

    AVAILABLE_FETCHING_CRITERIA: Final[list[str]] = [
        MailFetchingCriteria.ALL,
        MailFetchingCriteria.UNSEEN,
        MailFetchingCriteria.RECENT,
        MailFetchingCriteria.NEW,
        MailFetchingCriteria.OLD,
        MailFetchingCriteria.FLAGGED,
        MailFetchingCriteria.DRAFT,
        MailFetchingCriteria.ANSWERED,
        MailFetchingCriteria.DAILY,
        MailFetchingCriteria.WEEKLY,
        MailFetchingCriteria.MONTHLY,
        MailFetchingCriteria.ANNUALLY,
    ]
    """List of all criteria available for fetching. Refers to :class:`MailFetchingCriteria`.
    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4.
    """

    def makeFetchingCriterion(self, criterionName: str) -> str | None:
        """Returns the formatted criterion for the IMAP request, handles dates in particular.

        Args:
            criterionName: The criterion to prepare for the IMAP request.
                If not in :attr:`AVAILABLE_FETCHING_CRITERIA`, returns None.

        Returns:
            Formatted criterion to be used in IMAP request;
            None if `criterionName` is not in :attr:`AVAILABLE_FETCHING_CRITERIA`.
        """
        if criterionName == MailFetchingCriteria.DAILY:
            startTime = timezone.now() - datetime.timedelta(days=1)
        elif criterionName == MailFetchingCriteria.WEEKLY:
            startTime = timezone.now() - datetime.timedelta(weeks=1)
        elif criterionName == MailFetchingCriteria.MONTHLY:
            startTime = timezone.now() - datetime.timedelta(weeks=4)
        elif criterionName == MailFetchingCriteria.ANNUALLY:
            startTime = timezone.now() - datetime.timedelta(weeks=52)
        else:
            return criterionName
        return "SENTSINCE " + imaplib.Time2Internaldate(startTime).split(" ")[0]

    @override
    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the IMAP connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        super().__init__(account)

        self.connectToHost()
        self.safe_login(self.account.mail_address, self.account.password)

    @override
    def connectToHost(self) -> None:
        """Opens the connection to the IMAP server using the credentials from :attr:`account`.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host}
        if port := self.account.mail_host_port:
            kwargs["port"] = port
        if timeout := self.account.timeout:
            kwargs["timeout"] = timeout
        try:
            self._mailClient = imaplib.IMAP4(**kwargs)
        except Exception as error:
            self.logger.exception(
                "An %s occured connecting to %s!",
                error.__class__.__name__,
                self.account,
            )
            raise MailAccountError(
                f"An {error.__class__.__name__} occured connecting to {self.account}!"
            ) from error
        self.logger.info("Successfully connected to %s.", str(self.account))

    @override
    def test(self, mailbox: MailboxModel | None = None) -> None:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether it can be opened and listed.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
            MailAccountError: If the account test fails because an error occurs or a bad response is returned.
            MailboxError: If the mailbox test fails because an error occurs or a bad response is returned testing the mailbox.
        """
        super().test(mailbox)

        self.logger.debug("Testing %s ...", str(self.account))
        self.safe_noop()
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            self.logger.debug("Testing %s ...", str(mailbox))
            self.safe_select(mailbox.name, readonly=True)
            self.safe_check()
            self.safe_unselect()
            self.logger.debug("Successfully tested %s.", str(mailbox))

    @override
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        criterion: str = MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        """Fetches and returns maildata from a mailbox based on a given criterion.

        Todo:
            Rewrite this into a generator.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails in the IMAP request.
                Defaults to :attr:`Emailkasten.MailFetchingCriteria.ALL`.

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
                If :attr:`criterion` is not in :attr:`IMAPFetcher.AVAILABLE_FETCHING_CRITERIA`.
            MailboxError: If an error occurs or a bad response is returned.
        """
        super().fetchEmails(mailbox, criterion)

        searchCriterion = self.makeFetchingCriterion(criterion)

        self.logger.debug(
            "Searching and fetching %s messages in %s...",
            searchCriterion,
            str(mailbox),
        )
        self.logger.debug("Opening mailbox %s ...", str(mailbox))
        self.safe_select(mailbox.name, readonly=True)
        self.logger.debug("Successfully opened mailbox.")

        self.logger.debug(
            "Searching %s messages in %s ...", searchCriterion, str(mailbox)
        )
        __, messageUIDs = self.safe_uid("SEARCH", searchCriterion)
        self.logger.info(
            "Found %s messages with uIDs %s in %s.",
            searchCriterion,
            messageUIDs,
            str(mailbox),
        )

        self.logger.debug(
            "Fetching %s messages in %s ...", searchCriterion, str(mailbox)
        )
        mailDataList = []
        for uID in messageUIDs[0].split():
            try:
                __, messageData = self.safe_uid("FETCH", uID, "(RFC822)")
            except FetcherError:
                self.logger.warning(
                    "Failed to fetch message %s from %s!",
                    uID,
                    str(mailbox),
                    exc_info=True,
                )
                continue
            mailDataList.append(messageData[0][1])
        self.logger.debug(
            "Successfully fetched %s messages from %s.",
            searchCriterion,
            str(mailbox),
        )

        self.logger.debug("Leaving mailbox %s ...", str(mailbox))
        self.safe_unselect()
        self.logger.debug("Successfully left mailbox.")

        self.logger.debug(
            "Successfully searched and fetched %s messages in %s.",
            searchCriterion,
            str(mailbox),
        )

        return mailDataList

    @override
    def fetchMailboxes(self) -> list[bytes]:
        """Retrieves and returns the data of the mailboxes in the account.

        Todo:
            Rewrite this into a generator.

        Returns:
            List of data of all mailboxes in the account. Empty if none are found.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Fetching mailboxes at %s ...", str(self.account))
        __, mailboxes = self.safe_list()
        self.logger.debug("Successfully fetched mailboxes in %s.", self.account)
        return mailboxes

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the IMAP server if it is open."""
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailClient is None:
            self.logger.debug("Connection to %s is already closed.", str(self.account))
            return
        self.safe_logout()
        self.logger.info("Successfully closed connection to %s.", str(self.account))
