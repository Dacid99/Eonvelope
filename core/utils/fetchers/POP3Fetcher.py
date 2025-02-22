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

import logging
import poplib
from typing import TYPE_CHECKING, Final, Literal

from typing_extensions import override

from core.utils.fetchers.BaseFetcher import BaseFetcher

from ... import constants
from ...constants import TestStatusCodes
from .exceptions import MailAccountError, MailboxError


if TYPE_CHECKING:
    from types import TracebackType

    from ...models.AccountModel import AccountModel
    from ...models.MailboxModel import MailboxModel


class POP3Fetcher(BaseFetcher):
    """Maintains a connection to the POP server and fetches data using :mod:`poplib`.

    Opens a connection to the POP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an POP host.

    Attributes:
        account (:class:`core.models.AccountModel`): The model of the account to be fetched from.
        logger (:class:`logging.Logger`): The logger for this instance.
        _mailhost (:class:`poplib.POP3`): The POP host this instance connects to.
    """

    PROTOCOL = constants.MailFetchingProtocols.POP3
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.POP3`."""

    AVAILABLE_FETCHING_CRITERIA: Final[list[str]] = [constants.MailFetchingCriteria.ALL]
    """List of all criteria available for fetching. Refers to :class:`constants.MailFetchingCriteria`."""

    @override
    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the POP connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        self.account = account

        self.logger = logging.getLogger(__name__)

        self.connectToHost()
        try:
            self._mailhost.user(self.account.mail_address)
            self._mailhost.pass_(self.account.password)
        except poplib.error_proto:
            self.logger.exception(
                "A POP error occured connecting and logging in to %s!",
                self.account,
            )

    @override
    def connectToHost(self) -> None:
        """Opens the connection to the POP server using the credentials from :attr:`account`."""
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host}
        if port := self.account.mail_host_port:
            kwargs["port"] = port
        if timeout := self.account.timeout:
            kwargs["timeout"] = timeout
        try:
            self._mailhost = poplib.POP3(**kwargs)
        except Exception as error:
            self.logger.exception(
                "An IMAP error occured connecting to %s!",
                self.account,
            )
            raise MailAccountError from error
        self.logger.debug("Successfully connected to %s.", str(self.account))

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open."""
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info(
                    "Successfully closed connection to %s.", str(self.account)
                )
            except Exception:
                self.logger.exception(
                    "An unexpected error occured closing connection to %s!",
                    self.account,
                )
        else:
            self.logger.debug("Connection to %s was already closed.", str(self.account))

    @override
    def test(self, mailbox: MailboxModel | None = None) -> int:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether messages can be listed.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

        self.logger.debug("Testing %s ...", str(self.account))
        try:
            response = self._mailhost.noop()
            self._checkResponse(response)
            self.logger.debug("Successfully tested %s.", str(self.account))
        except poplib.error_proto as error:
            self.logger.exception(
                "An IMAP error occured during test of %s!",
                self.account,
            )
            raise MailAccountError from error

        if mailbox is not None:
            self.logger.debug("Testing %s ...", str(mailbox))

            try:
                response = self._mailhost.list()
                self._checkResponse(response)
            except poplib.error_proto as error:
                self.logger.exception(
                    "An IMAP error occured during test of %s!",
                    self.account,
                )
                raise MailboxError from error

    @override
    def fetchMailboxes(self) -> list[bytes]:
        """Returns the data of the mailboxes. For POP3 there is only one mailbox.

        Note:
            This method is built to match the methods from other fetcherclasses.

        Returns:
            The name of the mailbox in the account in a list.
        """
        return [b"INBOX"]

    @override
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        criterion: str = constants.MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        """Fetches and returns all maildata from the server.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].
            criterion: POP only support ALL lookups.
                Defaults to :attr:`Emailkasten.constants.MailFetchingCriteria.ALL`.
                Returns [] if a different value is passed.
                This arg ensures compatibility with the other fetchers.

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox. Empty if no messages are found or if an error occured.
        """
        if criterion != "ALL":
            return []

        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", str(mailbox), self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

        self.logger.debug("Fetching all messages in %s ...", str(mailbox))

        self.logger.debug("Listing all messages in %s ...", str(mailbox))
        try:
            status, messageNumbersList, _ = self._mailhost.list()
            if status != b"+OK":
                self.logger.error(
                    "Bad response listing mails in %s:\n %s, %s!",
                    str(mailbox),
                    status,
                    messageNumbersList,
                )
                mailbox.is_healthy = False
                mailbox.save(update_fields=["is_healthy"])
                return []

            messageCount = len(messageNumbersList)
            self.logger.debug("Found %s messages in %s.", messageCount, str(mailbox))

            self.logger.debug("Retrieving all messages in %s ...", str(mailbox))
            mailDataList = []

            for number in range(messageCount):
                status, messageData, _ = self._mailhost.retr(number + 1)
                if status != b"+OK":
                    self.logger.error(
                        "Bad response retrieving mail %s in %s:\n %s, %s",
                        number,
                        str(mailbox),
                        status,
                        messageData,
                    )
                    continue

                fullMessage = b"\n".join(messageData)
                mailDataList.append(fullMessage)

            self.logger.debug(
                "Successfully retrieved all messages in %s.", str(mailbox)
            )

        except poplib.error_proto:
            self.logger.error(
                "A POP error occured retrieving all messages in %s!",
                str(mailbox),
                exc_info=True,
            )
            mailbox.is_healthy = False
            mailbox.save(update_fields=["is_healthy"])
            return []
        except Exception:
            self.logger.error(
                "An unexpected error occured retrieving all messages in %s!",
                str(mailbox),
                exc_info=True,
            )
            return []

        self.logger.debug("Successfully fetched all messages in %s.", str(mailbox))

        mailbox.is_healthy = True
        mailbox.save(update_fields=["is_healthy"])

        return mailDataList
