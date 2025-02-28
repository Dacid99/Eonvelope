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

"""Module with the :class:`POP3_SSL_Fetcher` class."""

from __future__ import annotations

import poplib
from typing import TYPE_CHECKING, Final

from typing_extensions import override

from core.utils.fetchers.BaseFetcher import BaseFetcher
from core.utils.fetchers.SafePOPMixin import SafePOPMixin

from ...constants import MailFetchingCriteria, MailFetchingProtocols
from .exceptions import FetcherError, MailAccountError


if TYPE_CHECKING:
    from ...models.AccountModel import AccountModel
    from ...models.MailboxModel import MailboxModel


class POP3Fetcher(BaseFetcher, poplib.POP3, SafePOPMixin):
    """Maintains a connection to the POP server and fetches data using :mod:`poplib`.

    Opens a connection to the POP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an POP host.

    Since POP does not have any mailboxes, none of the methods should raise a `MailboxError`.

    Attributes:
        account (:class:`core.models.AccountModel`): The model of the account to be fetched from.
        logger (:class:`logging.Logger`): The logger for this instance.
        _mailClient (:class:`poplib.POP3`): The POP host this instance connects to.
    """

    PROTOCOL = MailFetchingProtocols.POP3
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA: Final[list[str]] = [MailFetchingCriteria.ALL]
    """List of all criteria available for fetching. Refers to :class:`MailFetchingCriteria`."""

    @override
    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the POP connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        super().__init__(account)

        self.connectToHost()
        self.safe_user(self.account.mail_address)
        self.safe_pass_(self.account.password)

    @override
    def connectToHost(self) -> None:
        """Opens the connection to the POP server using the credentials from :attr:`account`.

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
            self._mailClient = poplib.POP3(**kwargs)
        except Exception as error:
            self.logger.exception(
                "A POP error occured connecting to %s!",
                self.account,
            )
            raise MailAccountError from error
        self.logger.debug("Successfully connected to %s.", str(self.account))

    @override
    def test(self, mailbox: MailboxModel | None = None) -> None:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether messages can be listed.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
            MailAccountError: If the test fails because an error occurs or a bad response is returned.
        """
        if mailbox is not None and mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

        self.logger.debug("Testing %s ...", str(self.account))
        self.safe_noop()
        self.logger.debug("Successfully tested %s.", str(self.account))

        if mailbox is not None:
            self.logger.debug("Testing %s ...", str(mailbox))
            self.safe_list()
            self.logger.debug("Successfully tested %s.", str(mailbox))

    @override
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        criterion: str = MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        """Fetches and returns all maildata from the server.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: POP only support ALL lookups.
                Defaults to :attr:`Emailkasten.MailFetchingCriteria.ALL`.
                Returns [] if a different value is passed.
                This arg ensures compatibility with the other fetchers.

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
            MailAccountError: If an error occurs or a bad response is returned.
        """
        if criterion not in POP3Fetcher.AVAILABLE_FETCHING_CRITERIA:
            return []

        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

        self.logger.debug("Fetching all messages in %s ...", str(mailbox))

        self.logger.debug("Listing all messages in %s ...", str(mailbox))

        __, messageNumbersList, __ = self.safe_list()

        messageCount = len(messageNumbersList)
        self.logger.debug("Found %s messages in %s.", messageCount, str(mailbox))

        self.logger.debug("Retrieving all messages in %s ...", str(mailbox))
        mailDataList = []
        for number in range(messageCount):
            try:
                __, messageData, __ = self.safe_retr(number + 1)
            except FetcherError:
                continue

            fullMessage = b"\n".join(messageData)
            mailDataList.append(fullMessage)
        self.logger.debug("Successfully retrieved all messages in %s.", str(mailbox))

        self.logger.debug("Successfully fetched all messages in %s.", str(mailbox))

        return mailDataList

    @override
    def fetchMailboxes(self) -> list[bytes]:
        """Returns the data of the mailboxes. For POP3 there is only one mailbox named 'INBOX'.

        Note:
            This method is built to match the methods from other fetcherclasses.

        Returns:
            The name of the mailbox in the account in a list.
        """
        return [b"INBOX"]

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open.

        Ignores all exceptions that occur on logout.
        Otherwise a broken connection would raise additional exceptions, shadowing the cause of the exit.
        """
        super().close()
        try:
            self.safe_quit()
            self.logger.info("Successfully closed connection to %s.", str(self.account))
        except Exception:
            self.logger.exception(
                "An error occured closing connection to %s!",
                self.account,
            )
