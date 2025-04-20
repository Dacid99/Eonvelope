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

from collections.abc import Callable
from typing import Any

from django.utils.translation import gettext as _

from core.utils.fetchers.exceptions import FetcherError, MailAccountError, MailboxError


class SafeIMAPMixin:
    """Mixin with safe IMAP operations.

    The implementing class must have
    an :attr:`_mailClient` that is an :class:`imaplib.IMAP4` or :class:`imaplib.IMAP4_SSL`
    and an instance logger.

    Only errors leading up to and during the fetching process raise outside of the class.
    Otherwise issues with logout etc would destroy the work done with fetching, which makes no sense.

    """

    def checkResponse(
        self,
        response: tuple[str | bytes],
        commandName: str,
        expectedStatus: str = "OK",
        exception: type[FetcherError] | None = FetcherError,
    ) -> None:
        """Checks the status response of an IMAP action.

        If it doesnt match the expectation raises an exception.

        :class:`imaplib.IMAP4` typically responds in form of `tuple(status: str, data: list[bytes])`
        If the status is not as expected the data part contains debug info.

        Todo:
            Safely! extract error message from response for logging and exception.

        Args:
            response: The complete response to the IMAP action.
            commandName: The name of the action.
            expectedStatus: The expected status response. Defaults to `"OK"`.
            exception: The expection to raise if the status doesnt match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.

        Raises:
            exception: If the response status doesnt match the expectation.
        """
        if response[0] != expectedStatus:
            self.logger.error(
                "Bad server response for %s:\n%s",
                commandName,
                response,
            )
            if exception is not None:
                raise exception(
                    _("Bad server response for %(commandName)s:\n%(response)s")
                    % {"commandName": commandName, "response": response}
                )
        self.logger.debug("Server responded %s as expected.", response[0])

    @staticmethod
    def safe(
        expectedStatus: str = "OK",
        exception: type[FetcherError] = FetcherError | None,
    ) -> Callable:
        """Wrapper for IMAP actions.

        Catches expected errors, checks for correct responses and raises an FetcherError in case.

        Args:
            expectedStatus: The expected status response. Defaults to `"OK"`.
            exception: The exception to raise if an error occurs or the status doesnt match the expectation.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
                If None is passed, no exception is passed, all errors are logged nonetheless.

        Returns:
            The return value of the wrapped action.
            None if an exception occurs and :attr:`exception` is None.

        Raises:
            exception: If an error occurs or the status doesnt match the expectation.
        """

        def safeWrapper(imapAction: Callable) -> Callable:
            def safeAction(self, *args: Any, **kwargs: Any) -> Any:
                try:
                    response = imapAction(self, *args, **kwargs)
                except Exception as error:
                    self.logger.exception(
                        "An %s occured during %s!",
                        error.__class__.__name__,
                        imapAction.__name__,
                    )
                    if exception is not None:
                        raise exception(
                            _("An %(error_class_name)s occured during %(action_name)s!")
                            % {
                                "error_class_name": error.__class__.__name__,
                                "action_name": imapAction.__name__,
                            },
                        ) from error
                    return None
                else:
                    self.checkResponse(
                        response, imapAction.__name__, expectedStatus, exception
                    )
                    return response

            return safeAction

        return safeWrapper

    @safe(exception=MailAccountError)
    def safe_login(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.login`."""
        return self._mailClient.login(*args, **kwargs)

    @safe(exception=MailboxError)
    def safe_select(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.select`."""
        return self._mailClient.select(*args, **kwargs)

    @safe(exception=None)
    def safe_unselect(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.select`."""
        return self._mailClient.unselect(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_list(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.list`."""
        return self._mailClient.list(*args, **kwargs)

    @safe(exception=MailboxError)
    def safe_uid(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.uid`."""
        return self._mailClient.uid(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_noop(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.noop`."""
        return self._mailClient.noop(*args, **kwargs)

    @safe(exception=MailboxError)
    def safe_check(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.check`."""
        return self._mailClient.check(*args, **kwargs)

    @safe("BYE", exception=None)
    def safe_logout(self, *args: Any, **kwargs: Any) -> Any:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.logout`."""
        return self._mailClient.logout(*args, **kwargs)
