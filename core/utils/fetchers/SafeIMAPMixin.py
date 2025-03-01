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

"""Module with the SafeIMAPMixin mixin."""

import imaplib
from collections.abc import Callable
from typing import Any

from core.utils.fetchers.exceptions import FetcherError, MailAccountError, MailboxError


class SafeIMAPMixin:
    """Mixin with safe IMAP operations.

    The implementing class must have
    an :attr:`_mailClient` that is an :class:`imaplib.IMAP4` or :class:`imaplib.IMAP4_SSL`
    and an instance logger.
    """

    def checkResponse(
        self,
        response: tuple[str | bytes],
        commandName: str,
        expectedStatus: str = "OK",
        exception: type[FetcherError] = FetcherError,
    ) -> None:
        """Checks the status response of an IMAP action.

        If it doesnt match the expectation raises an exception.

        Args:
            response: The complete response to the IMAP action.
            commandName: The name of the action.
            expectedStatus: The expected status response. Defaults to `"OK"`.
            exception: The expection to raise if the status doesnt match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.

        Raises:
            exception: If the response status doesnt match the expectation.
        """
        status = response[0]
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

    @staticmethod
    def safe(
        expectedStatus: str = "OK",
        exception: type[FetcherError] = FetcherError,
    ) -> Callable:
        """Wrapper for IMAP actions.

        Catches expected errors and checks for correct responses and raises an FetcherError.

        Args:
            imapAction: The IMAP action to wrap.
            expectedStatus: The expected status response. Defaults to `"OK"`.
            exception: The exception to raise if an error occurs or the status doesnt match the expectation.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.

        Returns:
            The return value of the wrapped action.

        Raises:
            exception: If an error occurs or the status doesnt match the expectation.
        """

        def safeWrapper(imapAction: Callable) -> Callable:
            def safeAction(self, *args: Any, **kwargs: Any) -> Any:
                try:
                    response = imapAction(self, *args, **kwargs)
                except imaplib.IMAP4.error as error:
                    self.logger.exception(
                        "An IMAP error occured during %s!",
                        imapAction.__name__,
                    )
                    raise exception(
                        f"An IMAP error occured during {imapAction.__name__}!",
                    ) from error
                self.checkResponse(
                    response, imapAction.__name__, expectedStatus, exception
                )
                return response

            return safeAction

        return safeWrapper

    @safe(exception=MailAccountError)
    def safe_login(self, *args, **kwargs):
        return self._mailClient.login(*args, **kwargs)

    @safe(exception=MailboxError)
    def safe_select(self, *args, **kwargs):
        return self._mailClient.select(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_list(self, *args, **kwargs):
        return self._mailClient.list(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_uid(self, *args, **kwargs):
        return self._mailClient.uid(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_noop(self, *args, **kwargs):
        return self._mailClient.noop(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_check(self, *args, **kwargs):
        return self._mailClient.check(*args, **kwargs)

    @safe("BYE", exception=MailAccountError)
    def safe_logout(self, *args, **kwargs):
        return self._mailClient.logout(*args, **kwargs)
