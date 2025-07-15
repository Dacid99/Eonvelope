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

from ...constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from .BaseFetcher import BaseFetcher
from .exceptions import FetcherError, MailAccountError
from .SafePOPMixin import SafePOPMixin


if TYPE_CHECKING:
    from ...models.Account import Account
    from ...models.Mailbox import Mailbox


class POP3Fetcher(BaseFetcher, poplib.POP3, SafePOPMixin):
    """Maintains a connection to the POP server and fetches data using :mod:`poplib`.

    Opens a connection to the POP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an POP host.

    Since POP does not have any mailboxes, none of the methods should raise a `MailboxError`.
    """

    PROTOCOL = EmailProtocolChoices.POP3.value
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA: ClassVar[list[str]] = [
        EmailFetchingCriterionChoices.ALL.value
    ]
    """List of all criteria available for fetching. Refers to :class:`MailFetchingCriteria`."""

    @override
    def __init__(self, account: Account) -> None:
        """Constructor, starts the POP connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        super().__init__(account)

        self.connect_to_host()
        self.safe_user(self.account.mail_address)
        self.safe_pass_(self.account.password)

    @override
    def connect_to_host(self) -> None:
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
                self._mail_client = poplib.POP3(
                    host=mail_host, port=mail_host_port, timeout=timeout
                )
            elif mail_host_port:
                self._mail_client = poplib.POP3(host=mail_host, port=mail_host_port)
            elif timeout:
                self._mail_client = poplib.POP3(host=mail_host, timeout=timeout)
            else:
                self._mail_client = poplib.POP3(host=mail_host)
        except Exception as error:
            self.logger.exception(
                "A POP error occurred connecting to %s!",
                self.account,
            )
            raise MailAccountError(
                f"An {error.__class__.__name__}: {error} occurred connecting to {self.account}!"
            ) from error
        self.logger.info("Successfully connected to %s.", self.account)

    @override
    def test(self, mailbox: Mailbox | None = None) -> None:
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
    def fetch_emails(
        self,
        mailbox: Mailbox,
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

        super().fetch_emails(mailbox, criterion)

        self.logger.debug("Listing all messages in %s ...", mailbox)

        _, message_numbers_list, _ = self.safe_list()

        message_count = len(message_numbers_list)
        self.logger.info("Found %s messages in %s.", message_count, mailbox)

        self.logger.debug("Retrieving all messages in %s ...", mailbox)
        mail_data_list = []
        for number in range(message_count):
            try:
                _, message_data, _ = self.safe_retr(number + 1)
            except FetcherError:
                self.logger.warning(
                    "Failed to fetch message %s from %s!",
                    number,
                    mailbox,
                    exc_info=True,
                )
                continue

            full_message = b"\n".join(message_data)
            mail_data_list.append(full_message)
        self.logger.debug("Successfully retrieved all messages in %s.", mailbox)

        self.logger.debug("Successfully fetched all messages in %s.", mailbox)

        return mail_data_list

    @override
    def fetch_mailboxes(self) -> list[str]:
        """Returns the data of the mailboxes. For POP3 there is only one mailbox named 'INBOX'.

        Note:
            This method is built to match the fetcherclasses interface.

        Returns:
            The name of the mailbox in the account in a list.
        """
        return ["INBOX"]

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open."""
        self.logger.debug("Closing connection to %s ...", self.account)
        if self._mail_client is None:
            self.logger.debug("Connection to %s is already closed.", self.account)
            return
        self.safe_quit()
        self.logger.info("Successfully closed connection to %s.", self.account)
