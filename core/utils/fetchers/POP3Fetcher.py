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
from typing import TYPE_CHECKING, Literal

from ... import constants
from ...constants import TestStatusCodes

if TYPE_CHECKING:
    from types import TracebackType

    from ...models.AccountModel import AccountModel
    from ...models.MailboxModel import MailboxModel


class POP3Fetcher:
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

    AVAILABLE_FETCHING_CRITERIA = [constants.MailFetchingCriteria.ALL]
    """List of all criteria available for fetching. Refers to :class:`constants.MailFetchingCriteria`."""

    def __init__(self, account: AccountModel) -> None:
        """Constructor, starts the POP connection and logs into the account.
        If the connection could not be established the :attr:`account` is marked as unhealthy.
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
            self.account.save(update_fields=["is_healthy"])
        except poplib.error_proto:
            self.logger.error(
                "A POP error occured connecting and logging in to %s!",
                str(self.account),
                exc_info=True,
            )
            self.account.is_healthy = False
            self.account.save(update_fields=["is_healthy"])
            self.logger.info("Marked %s as unhealthy", str(self.account))
        except Exception:
            self.logger.error(
                "An unexpected error occured connecting and logging in to %s!",
                str(self.account),
                exc_info=True,
            )
            self.account.is_healthy = False
            self.account.save(update_fields=["is_healthy"])
            self.logger.info("Marked %s as unhealthy", str(self.account))

    def connectToHost(self) -> None:
        """Opens the connection to the POP server using the credentials from :attr:`account`."""
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host}
        if port := self.account.mail_host_port:
            kwargs["port"] = port
        if timeout := self.account.timeout:
            kwargs["timeout"] = timeout

        self._mailhost = poplib.POP3(**kwargs)
        self.logger.debug("Successfully connected to %s.", str(self.account))

    def login(self) -> None:
        """Logs into the target account using credentials from :attr:`account`."""
        self.logger.debug("Logging into %s ...", str(self.account))
        self._mailhost.user(self.account.mail_address)
        self._mailhost.pass_(self.account.password)
        self.logger.debug("Successfully logged into %s.", str(self.account))

    def close(self) -> None:
        """Logs out of the account and closes the connection to the POP server if it is open."""
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info(
                    "Successfully closed connection to %s.", str(self.account)
                )
            except poplib.error_proto:
                self.logger.error(
                    "A POP error occured to closing connection to %s!",
                    str(self.account),
                    exc_info=True,
                )
            except Exception:
                self.logger.error(
                    "An unexpected error occured closing connection to %s!",
                    str(self.account),
                    exc_info=True,
                )
        else:
            self.logger.debug("Connection to %s was already closed.", str(self.account))

    def test(self, mailbox: MailboxModel | None = None) -> int:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether messages can be listed.
        Sets the The :attr:`core.models.MailboxModel.is_healthy` flag accordingly.

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

            if status != b"+OK":
                self.logger.error(
                    "Bad response testing %s:\n %s, %s",
                    str(self.account),
                    status,
                    response,
                )
                self.account.is_healthy = False
                self.account.save(update_fields=["is_healthy"])

                return TestStatusCodes.BAD_RESPONSE

            self.account.is_healthy = True
            self.account.save(update_fields=["is_healthy"])
            self.logger.debug("Successfully tested %s.", str(self.account))

            if mailbox is not None:
                self.logger.debug("Testing %s ...", str(mailbox))

                status, response, _ = self._mailhost.list()

                if status != b"+OK":
                    self.logger.error(
                        "Bad response listing %s:\n %s, %s",
                        str(mailbox),
                        status,
                        response,
                    )
                    mailbox.is_healthy = False
                    mailbox.save(update_fields=["is_healthy"])

                    return TestStatusCodes.BAD_RESPONSE

                mailbox.is_healthy = True
                mailbox.save(update_fields=["is_healthy"])
                self.logger.debug("Successfully tested %s ...", str(mailbox))

            return TestStatusCodes.OK

        except poplib.error_proto:
            self.logger.error(
                "An IMAP error occured during test of %s!",
                str(self.account),
                exc_info=True,
            )
            self.account.is_healthy = False
            self.account.save(update_fields=["is_healthy"])
            return TestStatusCodes.ERROR
        except Exception:
            self.logger.error(
                "An unexpected error occured during test of %s!",
                str(self.account),
                exc_info=True,
            )
            return TestStatusCodes.UNEXPECTED_ERROR

    def fetchMailboxes(self) -> list[bytes]:
        """Returns the data of the mailboxes. For POP3 there is only one mailbox.

        Note:
            This method is built to match the methods from other fetcherclasses.

        Returns:
            The name of the mailbox in the account in a list.
        """
        return [b"INBOX"]

    def fetchEmails(
        self,
        mailbox: MailboxModel,
        criterion: str = constants.MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        """Fetches and returns all maildata from the server.
        If an :class:`poplib.error_proto` occurs the mailbox is flagged as unhealthy.
        If a bad response is received when listing messages, it is flagged as unhealthy as well.
        In case of success the mailbox is flagged as healthy.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
                If a mailbox that is not in the account is given, returns [].
            criterion: POP only support ALL lookups.
                Defaults to :attr:`Emailkasten.constants.MailFetchingCriteria.ALL`.
                Returns [] if other value is passed.
                This arg ensures compatibility with the other fetchers.

        Returns:
            List of :class:`email.message.EmailMessage` mails in the mailbox. Empty if no messages are found or if an error occured.
        """
        if criterion != "ALL":
            return []

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

    def __enter__(self) -> POP3Fetcher:
        """Framework method for use of class in 'with' statement, creates an instance.

        Returns:
            The new POP3Fetcher instance.
        """
        self.logger.debug("%s._enter_", str(self.__class__.__name__))
        return self

    def __exit__(
        self,
        exc_type: BaseException | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[True]:
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
            self.logger.error(
                "Unexpected error %s occured!", exc_type, exc_info=exc_value
            )
        return True
