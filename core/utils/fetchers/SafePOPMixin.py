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

"""Module with the SafePOPMixin mixin."""

from collections.abc import Callable
from typing import Any

from django.utils.translation import gettext as _

from core.utils.fetchers.exceptions import FetcherError, MailAccountError


class SafePOPMixin:
    """Mixin with safe POP operations.

    The implementing class must have
    an :attr:`_mailClient` that is an :class:`poplib.POP3` or :class:`poplib.POP3_SSL`
    and an instance logger.

    Only errors leading up to and during the fetching process should raise outside of the class.
    Otherwise issues with logout etc would destroy the work done with fetching, which makes no sense.
    """

    def checkResponse(
        self,
        response: tuple[str | bytes],
        commandName: str,
        expectedStatus: bytes = b"+OK",
        exception: type[FetcherError] = FetcherError,
    ) -> None:
        """Checks the status response of a POP action.

        If it doesnt match the expectation raises an exception.

        :class:`poplib.POP3` typically returns data in form of `tuple(status: bytes, data: list[bytes])`,
        while a response without data, e.g. for user or in case of an error is just a single `bytes` object starting with the status.

        Todo:
            Safely! extract error message from response for logging and exception.

        Args:
            response: The complete response to the POP action.
            commandName: The name of the action.
            expectedStatus: The expected status response. Defaults to `"+OK"`.
            exception: The expection to raise if the status doesnt match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.

        Raises:
            exception: If the response status doesnt match the expectation.
        """
        status = response if isinstance(response, bytes) else response[0]
        if not status.startswith(expectedStatus):
            self.logger.error("Bad server response for %s:\n%s", commandName, response)
            if exception is not None:
                raise exception(
                    _("Bad server response for %(commandName)s:\n%(response)s")
                    % {"commandName": commandName, "response": response}
                )
        self.logger.debug("Server responded %s as expected.", status)

    @staticmethod
    def safe(
        expectedStatus: bytes = b"+OK",
        exception: type[FetcherError] = FetcherError,
    ) -> Callable:
        """Wrapper for POP actions.

        Catches expected errors and checks for correct responses and raises an FetcherError.

        Args:
            expectedStatus: The expected status response. Defaults to `"+OK"`.
            exception: The exception to raise if an error occurs or the status doesnt match the expectation.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
                If None is passed, no exception is passed, all errors are logged nonetheless.

        Returns:
            The return value of the wrapped action.

        Raises:
            exception: If an error occurs or the status doesnt match the expectation.
        """

        def safeWrapper(popAction: Callable) -> Callable:
            def safeAction(self, *args: Any, **kwargs: Any) -> Any:
                try:
                    response = popAction(self, *args, **kwargs)
                except Exception as error:
                    self.logger.exception(
                        "An %s occured during %s!",
                        error.__class__.__name__,
                        popAction.__name__,
                    )
                    if exception is not None:
                        raise exception(
                            _("An %(error_class_name)s occured during %(action_name)s!")
                            % {
                                "error_class_name": error.__class__.__name__,
                                "action_name": popAction.__name__,
                            },
                        ) from error
                    return None
                else:
                    self.checkResponse(
                        response, popAction.__name__, expectedStatus, exception
                    )
                return response

            return safeAction

        return safeWrapper

    @safe(exception=MailAccountError)
    def safe_user(self, *args, **kwargs):
        return self._mailClient.user(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_pass_(self, *args, **kwargs):
        return self._mailClient.pass_(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_noop(self, *args, **kwargs):
        return self._mailClient.noop(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_list(self, *args, **kwargs):
        return self._mailClient.list(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_retr(self, *args, **kwargs):
        return self._mailClient.retr(*args, **kwargs)

    @safe(exception=None)
    def safe_quit(self, *args, **kwargs):
        return self._mailClient.quit(*args, **kwargs)
