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

"""Module with the :class:`IMAP4_SSL_Fetcher` class."""

from __future__ import annotations

import imaplib
import ssl
from typing import override

from ... import constants
from .exceptions import MailAccountError
from .IMAP4Fetcher import IMAP4Fetcher


class IMAP4_SSL_Fetcher(  # noqa: N801  # naming consistent with IMAP4_SSL class
    IMAP4Fetcher
):
    """Subclass of :class:`core.utils.fetchers.IMAP4Fetcher`.

    Does the same things, just using IMAP4_SSL protocol.
    """

    PROTOCOL = constants.EmailProtocolChoices.IMAP4_SSL
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.IMAP4_SSL`."""

    @override
    def connect_to_host(self) -> None:
        """Overrides :func:`core.utils.fetchers.IMAP4Fetcher.connect_to_host` to use :class:`imaplib.IMAP4_SSL`.

        Important:
            Using ssl_context is urgently required, see https://www.pentagrid.ch/en/blog/python-mail-libraries-certificate-verification/ .

        """
        self.logger.debug("Connecting to %s ...", self.account)

        mail_host = self.account.mail_host
        mail_host_port = self.account.mail_host_port
        timeout = self.account.timeout
        ssl_context = ssl.create_default_context()
        try:
            if mail_host_port and timeout:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    port=mail_host_port,
                    timeout=timeout,
                    ssl_context=ssl_context,
                )
            elif mail_host_port:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    port=mail_host_port,
                    ssl_context=ssl_context,
                )
            elif timeout:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    timeout=timeout,
                    ssl_context=ssl_context,
                )
            else:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    ssl_context=ssl_context,
                )
        except Exception as error:
            self.logger.exception(
                "An %s occurred connecting to %s!",
                error.__class__.__name__,
                self.account,
            )
            raise MailAccountError(
                f"An {error.__class__.__name__} occurred connecting to {self.account}!"
            ) from error
        self.logger.info("Successfully connected to %s.", self.account)
