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
from typing import TYPE_CHECKING, Literal

from core.utils.fetchers.exceptions import FetcherError

from ...constants import MailFetchingCriteria


if TYPE_CHECKING:
    from types import TracebackType

    from core.models.AccountModel import AccountModel
    from core.models.MailboxModel import MailboxModel


class BaseFetcher(ABC):
    """Template class for the mailfetcher classes."""

    @abstractmethod
    def __init__(self, account: AccountModel):
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def connectToHost(self) -> None:
        pass

    @abstractmethod
    def test(self, mailboxModel: MailboxModel) -> None:
        pass

    @abstractmethod
    def fetchEmails(
        self,
        mailbox: MailboxModel,
        fetchingCriterion: str = MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        pass

    @abstractmethod
    def fetchMailboxes(self) -> list[bytes]:
        pass

    @abstractmethod
    def close(self) -> None:
        self.logger.debug("Closing connection to %s ...", str(self.account))
        if self._mailhost is None:
            self.logger.debug("Connection to %s is already closed.", str(self.account))
            return

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
    ) -> Literal[False]:
        """Framework method for use of class in 'with' statement, closes an instance.

        Args:
            exc_type: The exception type that raised close.
            exc_value: The exception value that raised close.
            traceback: The exception traceback that raised close.

        Returns:
            False, exceptions leave the with block.
        """
        if exc_value or exc_type:
            self.logger.error(
                "An error %s occured, exiting Fetcher!", exc_type, exc_info=exc_value
            )
        self.close()
        return False
