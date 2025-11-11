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

"""Module with the SafeIMAPMixin mixin."""

import imaplib
import logging
from collections.abc import Callable
from typing import Any, Literal, Protocol, Self, TypeVar, overload

from core.utils.fetchers.exceptions import (
    BadServerResponseError,
    FetcherError,
    MailAccountError,
    MailboxError,
)


type IMAP4Response = tuple[
    str,
    str
    | list[bytes]
    | list[None]
    | list[Any]
    | list[bytes | None]
    | list[bytes | tuple[bytes, bytes]],
]

IMAP4ActionResponse = TypeVar("IMAP4ActionResponse", bound=IMAP4Response)


class IMAP4FetcherClass(Protocol):
    """Protocol defining the required attributes of a class implementing this mixin."""

    _mail_client: imaplib.IMAP4
    logger: logging.Logger


class SafeIMAPMixin:
    """Mixin with safe IMAP operations.

    The implementing class must have
    an :attr:`_mail_client` that is an :class:`imaplib.IMAP4` or :class:`imaplib.IMAP4_SSL`
    and an instance logger.

    Only errors leading up to and during the fetching process raise outside of the class.
    Otherwise issues with logout etc would destroy the work done with fetching, which makes no sense.

    """

    def check_response(
        self,
        response: IMAP4Response,
        command_name: str,
        exception_class: type[FetcherError] | None,
        expected_status: str = "OK",
    ) -> None:
        """Checks the status response of an IMAP action.

        If it doesn't match the expectation raises an exception.

        Todo:
            Safely! extract error message from response for logging and exception.

        Args:
            response: The complete response to the IMAP action.
            command_name: The name of the action.
            exception_class: The exception to raise if the status doesn't match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
            expected_status: The expected status response. Defaults to `"OK"`.

        Raises:
            exception_class: If the response status doesn't match the expectation.
        """
        status = response[0]
        if status != expected_status:
            self.logger.error(
                "Bad server response for %s:\n%s",
                command_name,
                response,
            )
            if exception_class is not None:
                raise exception_class(BadServerResponseError(response), command_name)
        self.logger.debug(
            "Server responded %s to %s as expected.",
            expected_status,
            command_name,
        )

    @overload
    @staticmethod
    def safe(
        exception_class: type[FetcherError],
        expected_status: str = "OK",
    ) -> Callable[
        [Callable[..., IMAP4ActionResponse]], Callable[..., IMAP4ActionResponse]
    ]: ...

    @overload
    @staticmethod
    def safe(
        exception_class: None,
        expected_status: str = "OK",
    ) -> Callable[
        [Callable[..., IMAP4ActionResponse]], Callable[..., IMAP4ActionResponse | None]
    ]: ...

    @staticmethod
    def safe(
        exception_class: type[FetcherError] | None,
        expected_status: str = "OK",
    ) -> Callable[
        [Callable[..., IMAP4ActionResponse]], Callable[..., IMAP4ActionResponse | None]
    ]:
        """Wrapper for IMAP actions.

        Catches expected errors, checks for correct responses and raises an FetcherError in case.

        Todo:
            Find a better way to disable the exception and getting rid of the typing mess.

        Args:
            exception_class: The exception class to raise if an error occurs or the status doesn't match the expectation.
                Must be a subclass of :class:`core.utils.fetchers.exceptions.FetcherError`.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
                If `None` is passed, no exception is raised, all errors are logged nonetheless.
            expected_status: The expected status response. Defaults to `"OK"`.

        Returns:
            The return value of the wrapped action.
            None if an error occurs and `exception` is `None`.

        Raises:
            exception_class: If an error occurs or the status doesn't match the expectation.
        """

        def safe_wrapper(
            imap_action: Callable[..., IMAP4ActionResponse],
        ) -> Callable[..., IMAP4ActionResponse | None]:
            def safe_action(
                self: Self, *args: Any, **kwargs: Any
            ) -> IMAP4ActionResponse | None:
                try:
                    response = imap_action(self, *args, **kwargs)
                except Exception as error:
                    self.logger.exception(
                        "Error during %s!",
                        imap_action.__name__,
                    )
                    if exception_class is not None:
                        raise exception_class(error, imap_action.__name__) from error
                    return None
                else:
                    self.check_response(
                        response, imap_action.__name__, exception_class, expected_status
                    )
                    return response

            return safe_action

        return safe_wrapper

    @safe(exception_class=MailAccountError)
    def safe_login(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[Literal["OK"], list[bytes]] | tuple[str, str]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.login`.

        In case the passwords contains utf-8 chars, use authenticate instead.

        References:
            https://github.com/ikvk/imap_tools/pull/186/commits/0ce6b47a0019538e22a977516e28df16ea0a7961
        """
        try:
            response = self._mail_client.login(*args, **kwargs)
        except UnicodeEncodeError:
            credentials = (
                b"\0" + args[0].encode("utf-8") + b"\0" + args[1].encode("utf-8")
            )
            response = self._mail_client.authenticate(
                "PLAIN",
                lambda x: credentials,  # noqa: ARG005 ;  authenticate method needs a callable that takes a single arg
            )
        return response

    @safe(exception_class=MailboxError)
    def safe_select(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[bytes | None]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.select`."""
        return self._mail_client.select(*args, **kwargs)

    @safe(exception_class=None)
    def safe_unselect(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[Any]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.select`."""
        return self._mail_client.unselect(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_list(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[None] | list[bytes | tuple[bytes, bytes]]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.list`."""
        return self._mail_client.list(*args, **kwargs)

    @safe(exception_class=MailboxError)
    def safe_uid(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[Any]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.uid`."""
        return self._mail_client.uid(*args, **kwargs)

    @safe(exception_class=MailAccountError)
    def safe_noop(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[bytes]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.noop`."""
        return self._mail_client.noop(*args, **kwargs)

    @safe(exception_class=MailboxError)
    def safe_check(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[Any]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.check`."""
        return self._mail_client.check(*args, **kwargs)

    @safe(exception_class=MailboxError)
    def safe_append(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[Any]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.append`."""
        return self._mail_client.append(*args, **kwargs)

    @safe(exception_class=None, expected_status="BYE")
    def safe_logout(
        self: IMAP4FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[str, list[None] | list[bytes | tuple[bytes, bytes]]]:
        """The :func:`safe` wrapped version of :func:`imaplib.IMAP4.logout`."""
        return self._mail_client.logout(*args, **kwargs)
