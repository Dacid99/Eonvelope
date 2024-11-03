# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import poplib

from .. import constants
from .POP3Fetcher import POP3Fetcher


class POP3_SSL_Fetcher(POP3Fetcher): 
    """Subclass of :class:`Emailkasten.Fetchers.POP3_Fetcher`.

    Does the same things, just using POP3_SSL protocol.
    """

    PROTOCOL = constants.MailFetchingProtocols.POP3_SSL


    def connectToHost(self):
        """Overrides `connectToHost` from `POP3Fetcher` to use :class:`poplib.POP3_SSL`."""
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = poplib.POP3_SSL(host=self.account.mail_host, port=self.account.mail_host_port, context=None, timeout=None)
        self.logger.debug("Success")

    
    @staticmethod
    def test(account):
        """Overrides `test` from `POP3Fetcher` to use :class:`poplib.POP3_SSL`."""
        with POP3_SSL_Fetcher(account) as pop3sslFetcher:
            return bool(pop3sslFetcher)

