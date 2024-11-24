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
from ..Models.AccountModel import AccountModel
from ..Models.MailboxModel import MailboxModel


class POP3_SSL_Fetcher(POP3Fetcher):
    """Subclass of :class:`Emailkasten.Fetchers.POP3Fetcher`.

    Does the same things, just using POP3_SSL protocol.
    """

    PROTOCOL = constants.MailFetchingProtocols.POP3_SSL
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.POP3_SSL`."""


    def connectToHost(self) -> None:
        """Overrides :func:`Emailkasten.Fetchers.POP3Fetcher.connectToHost` to use :class:`poplib.POP3_SSL`."""
        self.logger.debug("Connecting to %s ...", str(self.account))

        kwargs = {"host": self.account.mail_host,
                  "context": None}
        if (port := self.account.mail_host_port):
            kwargs["port"] = port
        if (timeout := self.account.timeout):
            kwargs["timeout"] = timeout

        self._mailhost = poplib.POP3_SSL(**kwargs)

        self.logger.debug("Successfully connected to %s.", str(self.account))


    @staticmethod
    def testAccount(account: AccountModel) -> int:
        """Overrides :func:`Emailkasten.Fetchers.POP3Fetcher.testAccount` to use :class:`poplib.POP3_SSL`.

        Args:
            account: Data of the account to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with POP3_SSL_Fetcher(account) as pop3sslFetcher:
            result = pop3sslFetcher.test()
        return result

    @staticmethod
    def testMailbox(mailbox: MailboxModel) -> int:
        """Overrides :func:`Emailkasten.Fetchers.POP3Fetcher.testMailbox` to use :class:`poplib.POP3_SSL`.

        Args:
            mailbox: Data of the mailboc to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with POP3_SSL_Fetcher(mailbox.account) as pop3sslFetcher:
            result = pop3sslFetcher.test(mailbox=mailbox)
        return result
