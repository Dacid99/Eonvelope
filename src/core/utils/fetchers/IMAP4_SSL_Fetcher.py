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

"""Module with the :class:`IMAP4_SSL_Fetcher` class."""

from __future__ import annotations

import imaplib
import ssl
from typing import override

from django.utils.translation import gettext_lazy as _

from core import constants

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
            if mail_host_port:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    port=mail_host_port,
                    timeout=timeout,
                    ssl_context=ssl_context,
                )
            else:
                self._mail_client = imaplib.IMAP4_SSL(
                    host=mail_host,
                    timeout=timeout,
                    ssl_context=ssl_context,
                )
        except Exception as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error, _("connecting")) from error
        self.logger.info("Successfully connected to %s.", self.account)
