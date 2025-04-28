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

"""Module with the :class:`POP3_SSL_Fetcher` class."""

from __future__ import annotations

import poplib
from typing import override

from ... import constants
from .exceptions import MailAccountError
from .POP3Fetcher import POP3Fetcher


class POP3_SSL_Fetcher(POP3Fetcher):
    """Subclass of :class:`core.utils.fetchers.POP3Fetcher`.

    Does the same things, just using POP3_SSL protocol.
    """

    PROTOCOL = constants.EmailProtocolChoices.POP3_SSL
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.POP3_SSL`."""

    @override
    def connectToHost(self) -> None:
        """Overrides :func:`core.utils.fetchers.POP3Fetcher.connectToHost` to use :class:`poplib.POP3_SSL`."""
        self.logger.debug("Connecting to %s ...", self.account)

        mail_host = self.account.mail_host
        mail_host_port = self.account.mail_host_port
        timeout = self.account.timeout
        try:
            if mail_host_port and timeout:
                self._mailClient = poplib.POP3_SSL(
                    host=mail_host, port=mail_host_port, timeout=timeout, context=None
                )
            elif mail_host_port:
                self._mailClient = poplib.POP3_SSL(
                    host=mail_host, port=mail_host_port, context=None
                )
            elif timeout:
                self._mailClient = poplib.POP3_SSL(
                    host=mail_host, timeout=timeout, context=None
                )
            else:
                self._mailClient = poplib.POP3_SSL(host=mail_host, context=None)
        except Exception as error:
            self.logger.exception(
                "A POP error occured connecting to %s!",
                self.account,
            )
            raise MailAccountError(
                f"An {error.__class__.__name__} occured connecting to {self.account}!"
            ) from error
        self.logger.info("Successfully connected to %s.", self.account)
