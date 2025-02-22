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
from ...constants import MailFetchingCriteria
import logging
from typing import TYPE_CHECKING, Any, Literal

from core.utils.fetchers.exceptions import FetcherError


if TYPE_CHECKING:
    from types import TracebackType

    from core.models.AccountModel import AccountModel
    from core.models.MailboxModel import MailboxModel


class BaseFetcher:
    """Template class for the mailfetcher classes."""

    def _checkResponse(
        self,
        response: tuple[str | bytes],
        exception: type[FetcherError] = FetcherError,
        commandName: str = "",
        expectedStatus: str = "OK",
    ) -> None:
        status = (
            response[0].decode("utf-8", errors="replace")
            if isinstance(response[0], bytes)
            else response[0]
        )
        if status != expectedStatus:
            serverMessage = (
                response[1].decode("utf-8", errors="replace")
                if response[1] and isinstance(response[1], bytes)
                else "Unknown Error"
            )
            self.logger.error(
                "Bad server response for %s:\n%s %s",
                commandName,
                status,
                serverMessage,
            )
            raise exception(f"Bad server response for {commandName}:\n{serverMessage}")
        self.logger.debug("Server responded %s as expected.", status)

    def __init__(self, mailboxModel: MailboxModel):
        self.logger = logging.getLogger(__name__)
        raise NotImplementedError

    def connectToHost(self, accountModel: AccountModel) -> None:
        pass

    def fetchEmails(
        self,
        mailbox: MailboxModel,
        fetchingCriterion: str = MailFetchingCriteria.ALL,
    ) -> list[bytes]:
        pass

    def fetchMailboxes(self) -> list[bytes]:
        pass

    def test(self, mailboxModel: MailboxModel) -> bool:
        pass

    def close(self) -> None:
        pass

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
