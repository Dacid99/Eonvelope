# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the :class:`BaseFetcher` class template."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self, override

from core.constants import EmailFetchingCriterionChoices


if TYPE_CHECKING:
    from types import TracebackType

    from core.models.Account import Account
    from core.models.Email import Email
    from core.models.Mailbox import Mailbox


class BaseFetcher(ABC):
    """Template class for the mailfetcher classes.

    Provides arg-checking for methods.
    """

    PROTOCOL = ""
    """Name of the used protocol, should be one of :class:`MailFetchingProtocols`."""

    AVAILABLE_FETCHING_CRITERIA: tuple[str, ...] = ("",)
    """Tuple of all criteria available for fetching. Should refer to :class:`MailFetchingCriteria`. Must be immutable!"""

    @abstractmethod
    def __init__(self, account: Account) -> None:
        """Constructor basis, sets up the instance logger.

        Args:
            account: The model of the account to fetch from.
        """
        self.account = account
        self.logger = logging.getLogger(self.__module__)
        if account.protocol != self.PROTOCOL:
            self.logger.error(
                "The protocol of %s is not implemented by fetcher %s!",
                account,
                self.__class__.__name__,
            )
            raise ValueError(
                f"The protocol of {account} is not implemented by fetcher {self.__class__.__name__}!"
            )

    @abstractmethod
    def connect_to_host(self) -> None:
        """Opens the connection to the mailserver."""

    @abstractmethod
    def test(self, mailbox: Mailbox | None = None) -> None:
        """Tests the connection to the mailaccount and, if given, the mailbox.

        Args:
            mailbox: The mailbox to be tested. Default is `None`.

        Raises:
            ValueError: If the `mailbox` argument does not belong to :attr:`self.account`.
        """
        if mailbox is not None and mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", mailbox, self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

    @abstractmethod
    def fetch_emails(  # type: ignore[return]  # this abstractmethod just provides basic arg-checking
        self,
        mailbox: Mailbox,
        criterion: str = EmailFetchingCriterionChoices.ALL,
        criterion_arg: str = "",
    ) -> list[bytes]:
        """Fetches emails based on a criterion from the server.

        Args:
            mailbox: The model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails by.
                Defaults to :attr:`core.constants.EmailFetchingCriterionChoices.ALL`.
            criterion_arg: The value to filter by.
                Defaults to "" as :attr:`core.constants.EmailFetchingCriterionChoices.ALL` does not require a value.

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.

        Raises:
            ValueError: If the :attr:`fetching_criterion` is not available for this fetcher.
        """
        if criterion not in self.AVAILABLE_FETCHING_CRITERIA:
            self.logger.error(
                "Fetching by %s is not available via protocol %s!",
                criterion,
                self.PROTOCOL,
            )
            raise ValueError(
                f"Fetching by {criterion} is not available via protocol {self.PROTOCOL}!"
            )
        if mailbox.account != self.account:
            self.logger.error("%s is not a mailbox of %s!", mailbox, self.account)
            raise ValueError(f"{mailbox} is not in {self.account}!")

    @abstractmethod
    def fetch_mailboxes(self) -> list[bytes] | list[str]:
        """Fetches all mailbox names from the server.

        Returns:
            List of data of all mailboxes in the account. Empty if none are found.
        """

    @abstractmethod
    def restore(self, email: Email) -> None:
        """Restores an email to a mailbox.

        Args:
            email: The email to restore.

        Raises:
            ValueError: If the emails mailbox is not in this fetchers account.
            FileNotFoundError: If the emails file_path is not set.
        """
        if email.mailbox.account != self.account:
            self.logger.error("Mailbox of %s is not in %s!", email, self.account)
            raise ValueError(f"Mailbox of {email} is not in {self.account}!")
        if not email.file_path:
            raise FileNotFoundError("Email has no stored eml file.")

    @abstractmethod
    def close(self) -> None:
        """Closes the connection to the mail server."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the :class:`BaseFetcher` instances.

        Returns:
            The string representation of the fetcher instance.
        """
        return f"{self.__class__.__name__} for {self.account}"

    def __enter__(self) -> Self:
        """Framework method for use of class in 'with' statement, creates an instance.

        Returns:
            The new Fetcher instance.
        """
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Framework method for use of class in 'with' statement, closes an instance.

        Args:
            exc_type: The exception type that raised close.
            exc_value: The exception value that raised close.
            traceback: The exception traceback that raised close.
        """
        if exc_value or exc_type:
            self.logger.error(
                "An error %s occurred, exiting Fetcher!", exc_type, exc_info=exc_value
            )
        self.close()
