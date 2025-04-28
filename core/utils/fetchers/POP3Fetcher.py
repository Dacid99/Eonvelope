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
from typing import TYPE_CHECKING, ClassVar, override

from core.utils.fetchers.BaseFetcher import BaseFetcher
from core.utils.fetchers.SafePOPMixin import SafePOPMixin

from ...constants import EmailFetchingCriterionChoices, EmailProtocolChoices
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

    PROTOCOL = EmailProtocolChoices.POP3.value
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA: ClassVar[list[str]] = [
        EmailFetchingCriterionChoices.ALL.value
    ]
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
        self.logger.debug("Connecting to %s ...", self.account)

        mail_host = self.account.mail_host
        mail_host_port = self.account.mail_host_port
        timeout = self.account.timeout
        try:
            if mail_host_port and timeout:
                self._mailClient = poplib.POP3(
                    host=mail_host, port=mail_host_port, timeout=timeout
                )
            elif mail_host_port:
                self._mailClient = poplib.POP3(host=mail_host, port=mail_host_port)
            elif timeout:
                self._mailClient = poplib.POP3(host=mail_host, timeout=timeout)
            else:
                self._mailClient = poplib.POP3(host=mail_host)
        except Exception as error:
            self.logger.exception(
                "A POP error occured connecting to %s!",
                self.account,
            )
            raise MailAccountError(
                f"An {error.__class__.__name__} occured connecting to {self.account}!"
            ) from error
        self.logger.info("Successfully connected to %s.", self.account)

    @override
    def test(self, mailbox: MailboxModel | None = None) -> None:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether messages can be listed.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
            MailAccountError: If the test fails because an error occurs or a bad response is returned.
        """
        super().test(mailbox)

        self.logger.debug("Testing %s ...", self.account)
        self.safe_noop()
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            self.logger.debug("Testing %s ...", mailbox)
            self.safe_list()
            self.logger.debug("Successfully tested %s.", mailbox)

    @override
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        criterion: str = EmailFetchingCriterionChoices.ALL,
    ) -> list[bytes]:
        """Fetches and returns all maildata from the server.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: POP only supports ALL lookups.
                Defaults to :attr:`Emailkasten.MailFetchingCriteria.ALL`.
                This arg ensures compatibility with the other fetchers.

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
                If :attr:`criterion` is not :attr:`Emailkasten.MailFetchingCriteria.ALL`.
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Fetching all messages in %s ...", mailbox)

        super().fetchEmails(mailbox, criterion)

        self.logger.debug("Listing all messages in %s ...", mailbox)

        _, messageNumbersList, _ = self.safe_list()

        messageCount = len(messageNumbersList)
        self.logger.info("Found %s messages in %s.", messageCount, mailbox)

        self.logger.debug("Retrieving all messages in %s ...", mailbox)
        mailDataList = []
        for number in range(messageCount):
            try:
                _, messageData, _ = self.safe_retr(number + 1)
            except FetcherError:
                self.logger.warning(
                    "Failed to fetch message %s from %s!",
                    number,
                    mailbox,
                    exc_info=True,
                )
                continue

            fullMessage = b"\n".join(messageData)
            mailDataList.append(fullMessage)
        self.logger.debug("Successfully retrieved all messages in %s.", mailbox)

        self.logger.debug("Successfully fetched all messages in %s.", mailbox)

        return mailDataList

    @override
    def fetchMailboxes(self) -> list[bytes]:
        """Returns the data of the mailboxes. For POP3 there is only one mailbox named 'INBOX'.

        Note:
            This method is built to match the fetcherclasses interface.

        Returns:
            The name of the mailbox in the account in a list.
        """
        return [b"INBOX"]

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open."""
        self.logger.debug("Closing connection to %s ...", self.account)
        if self._mailClient is None:
            self.logger.debug("Connection to %s is already closed.", self.account)
            return
        self.safe_quit()
        self.logger.info("Successfully closed connection to %s.", self.account)
