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

"""Module with the :class:`IMAP_SSL_Fetcher` class."""
from __future__ import annotations

import imaplib

from ... import constants
from .IMAPFetcher import IMAPFetcher


class IMAP_SSL_Fetcher(IMAPFetcher):
    """Subclass of :class:`core.utils.fetchers.IMAPFetcher`.

    Does the same things, just using IMAP_SSL protocol.
    """

    PROTOCOL = constants.MailFetchingProtocols.IMAP_SSL
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.IMAP_SSL`."""

    def connectToHost(self) -> None:
        """Overrides :func:`core.utils.fetchers.IMAPFetcher.connectToHost` to use :class:`imaplib.IMAP4_SSL`."""
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host, "ssl_context": None}
        if port := self.account.mail_host_port:
            kwargs["port"] = port
        if timeout := self.account.timeout:
            kwargs["timeout"] = timeout

        self._mailhost = imaplib.IMAP4_SSL(**kwargs)
        self.logger.debug("Successfully connected to %s.", str(self.account))
