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

"""Module with the SafePOPMixin mixin."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, Self, TypeVar, overload

from core.utils.fetchers.exceptions import (
    BadServerResponseError,
    FetcherError,
    MailAccountError,
)

if TYPE_CHECKING:
    import logging
    import poplib
    from collections.abc import Callable

type POP3Response = bytes | tuple[bytes, list[bytes], int]

POP3ActionResponse = TypeVar("POP3ActionResponse", bound=POP3Response)


class POP3FetcherClass(Protocol):
    """Protocol defining the required attributes of a class implementing this mixin."""

    _mail_client: poplib.POP3
    logger: logging.Logger


class SafePOPMixin:
    """Mixin with safe POP operations.

    The implementing class must have
    an :attr:`_mail_client` that is an :class:`poplib.POP3` or :class:`poplib.POP3_SSL`
    and an instance logger.

    Only errors leading up to and during the fetching process should raise outside of the class.
    Otherwise issues with logout etc would destroy the work done with fetching, which makes no sense.
    """

    def check_response(
        self,
        response: POP3Response,
        command_name: str,
        exception_class: type[FetcherError] | None,
        expected_status: bytes = b"+OK",
    ) -> None:
        """Checks the status response of a POP action.

        If it doesn't match the expectation raises an exception.

        Todo:
            Safely! extract error message from response for logging and exception.

        Args:
            response: The complete response to the POP action.
            command_name: The name of the action.
            exception_class: The exception class to raise if the status doesn't match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
            expected_status: The expected status response. Defaults to `"+OK"`.

        Raises:
            exception_class: If the response status doesn't match the expectation.
        """
        status = response if isinstance(response, bytes) else response[0]
        if not status.startswith(expected_status):
            self.logger.error(
                "Bad server response for %s:\n%s",
                command_name,
                response,
            )
            if exception_class is not None:
                raise exception_class(BadServerResponseError(response), command_name)
        self.logger.debug(
            "Server responded %s to %s as expected.",
            status,
            command_name,
        )

    @overload
    @staticmethod
    def safe(
        exception_class: type[FetcherError],
        expected_status: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse]
    ]: ...

    @overload
    @staticmethod
    def safe(
        exception_class: None,
        expected_status: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse | None]
    ]: ...

    @staticmethod
    def safe(
        exception_class: type[FetcherError] | None,
        expected_status: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse | None]
    ]:
        """Wrapper for POP actions.

        Catches expected errors and checks for correct responses and raises an FetcherError.

        Todo:
            Find a better way to disable the exception and getting rid of the typing mess.

        Args:
            exception_class: The exception class to raise if an error occurs or the status doesn't match the expectation.
                Must be a subclass of :class:`core.utils.fetchers.exceptions.FetcherError`.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
                If `None` is passed, no exception is raised, all errors are logged nonetheless.
            expected_status: The expected status response. Defaults to `"+OK"`.

        Returns:
            The return value of the wrapped action.
            None if an error occurs and `exception` is `None`.

        Raises:
            exception_class: If an error occurs or the status doesn't match the expectation.
        """

        def safe_wrapper(
            pop_action: Callable[..., POP3ActionResponse],
        ) -> Callable[..., POP3ActionResponse | None]:
            def safe_action(
                self: Self, *args: Any, **kwargs: Any
            ) -> POP3ActionResponse | None:
                try:
                    response = pop_action(self, *args, **kwargs)
                except Exception as error:
                    self.logger.exception(
                        "Error during %s!",
                        pop_action.__name__,
                    )
                    if exception_class is not None:
                        raise exception_class(error, pop_action.__name__) from error
                    return None
                else:
                    self.check_response(
                        response, pop_action.__name__, exception_class, expected_status
                    )
                return response

            return safe_action

        return safe_wrapper

    @safe(exception_class=MailAccountError)
    def safe_user(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.user`."""
        return self._mail_client.user(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_pass_(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.pass_`."""
        return self._mail_client.pass_(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_noop(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.noop`."""
        return self._mail_client.noop(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_list(
        self: POP3FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[bytes, list[bytes], int]:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.list`."""
        return self._mail_client.list(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_retr(
        self: POP3FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[bytes, list[bytes], int]:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.retr`."""
        return self._mail_client.retr(*args, **kwargs)

    @safe(exception_class=None)
    def safe_quit(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.quit`."""
        return self._mail_client.quit(*args, **kwargs)
