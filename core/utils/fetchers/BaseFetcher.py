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

"""Module with the :class:`BaseFetcher` class template."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ...constants import MailFetchingCriteria


if TYPE_CHECKING:
    from types import TracebackType

    from core.models.AccountModel import AccountModel
    from core.models.MailboxModel import MailboxModel


class BaseFetcher(ABC):
    """Template class for the mailfetcher classes."""

    @abstractmethod
    def __init__(self, account: AccountModel):
        """Constructor basis, sets up the instance logger.

        Args:
            account: The model of the account to fetch from.
        """
        self.logger = logging.getLogger(self)
        self.account = account

    @abstractmethod
    def connectToHost(self) -> None:
        """Opens the connection to the mailserver."""

    @abstractmethod
    def test(self, mailboxModel: MailboxModel) -> None:
        """Tests the connection to the mailaccount and, if given, the mailbox.

        Args:
            mailbox: The mailbox to be tested. Default is `None`.
        """

    @abstractmethod
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        fetchingCriterion: str = MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        """Fetches emails based on a criterion from the server.

        Args:
            mailbox: The model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails by.
                Defaults to :attr:`Emailkasten.MailFetchingCriteria.ALL`.

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.
        """

    @abstractmethod
    def fetchMailboxes(self) -> list[bytes]:
        """Fetches all mailbox names from the server.

        Returns:
            List of data of all mailboxes in the account. Empty if none are found.
        """

    @abstractmethod
    def close(self) -> None:
        """Closes the connection to the mail server."""
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailClient is None:
            self.logger.debug("Connection to %s is already closed.", str(self.account))
            return

    def __str__(self) -> str:
        """Returns a string representation of the :class:`BaseFetcher` instances.

        Returns:
            The string representation of the fetcher instance.
        """
        return f"Fetcher for {self.account}"

    def __enter__(self) -> BaseFetcher:
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
                "An error %s occured, exiting Fetcher!", exc_type, exc_info=exc_value
            )
        self.close()
