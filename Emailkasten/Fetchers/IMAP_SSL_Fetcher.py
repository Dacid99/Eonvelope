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

import imaplib

from .. import constants
from .IMAPFetcher import IMAPFetcher
from ..Models.AccountModel import AccountModel
from ..Models.MailboxModel import MailboxModel


class IMAP_SSL_Fetcher(IMAPFetcher):
    """Subclass of :class:`Emailkasten.Fetchers.IMAPFetcher`.

    Does the same things, just using IMAP_SSL protocol.
    """

    PROTOCOL = constants.MailFetchingProtocols.IMAP_SSL
    """Name of the used protocol, refers to :attr:`constants.MailFetchingProtocols.IMAP_SSL`."""

    def connectToHost(self):
        """Overrides :func:`Emailkasten.Fetchers.IMAPFetcher.connectToHost` to use :class:`imaplib.IMAP4_SSL`."""
        self.logger.debug("Connecting to %s ...", str(self.account))
        kwargs = {"host": self.account.mail_host,
                  "ssl_context": None}
        if (port := self.account.mail_host_port):
            kwargs["port"] = port
        if (timeout := self.account.timeout):
            kwargs["timeout"] = timeout

        self._mailhost = imaplib.IMAP4_SSL(**kwargs)
        self.logger.debug("Successfully connected to %s.", str(self.account))


    @staticmethod
    def testAccount(account: AccountModel) -> int:
        """Overrides :func:`Emailkasten.Fetchers.IMAPFetcher.testAccount` to use :class:`imaplib.IMAP4_SSL`.

        Args:
            account: Data of the account to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with IMAP_SSL_Fetcher(account) as imapsslFetcher:
            result = imapsslFetcher.test()
        return result


    @staticmethod
    def testMailbox(mailbox: MailboxModel) -> int:
        """Overrides :func:`Emailkasten.Fetchers.IMAPFetcher.testMailbox` to use :class:`imaplib.IMAP4_SSL`.

        Args:
            mailbox: Data of the mailbox to be tested.

        Returns:
            The test status in form of a code from :class:`Emailkasten.constants.TestStatusCodes`.
        """
        with IMAP_SSL_Fetcher(mailbox.account) as imapsslFetcher:
            result = imapsslFetcher.test(mailbox)
        return result
