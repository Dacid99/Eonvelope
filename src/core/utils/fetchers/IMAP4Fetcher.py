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

"""Module with the :class:`IMAP4Fetcher` class."""

from __future__ import annotations

import imaplib
from itertools import batched
from typing import TYPE_CHECKING, override

from django.utils.translation import gettext_lazy as _
from imap_tools.imap_utf7 import utf7_encode

from core.constants import (
    EmailFetchingCriterionChoices,
    EmailProtocolChoices,
)
from core.utils.fetchers.exceptions import FetcherError, MailAccountError
from core.utils.fetchers.SafeIMAPMixin import SafeIMAPMixin
from core.utils.mail_parsing import parse_IMAP_mailbox_data

from .BaseFetcher import BaseFetcher

if TYPE_CHECKING:
    from core.models.Account import Account
    from core.models.Email import Email
    from core.models.Mailbox import Mailbox
    from core.utils import FetchingCriterion


class IMAP4Fetcher(BaseFetcher, SafeIMAPMixin):
    """Maintains a connection to the IMAP server and fetches data using :mod:`imaplib`.

    Opens a connection to the IMAP server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an IMAP host.
    """

    PROTOCOL = EmailProtocolChoices.IMAP4
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.IMAP`."""

    AVAILABLE_FETCHING_CRITERIA = (
        EmailFetchingCriterionChoices.ALL,
        EmailFetchingCriterionChoices.UNSEEN,
        EmailFetchingCriterionChoices.SEEN,
        EmailFetchingCriterionChoices.RECENT,
        EmailFetchingCriterionChoices.NEW,
        EmailFetchingCriterionChoices.OLD,
        EmailFetchingCriterionChoices.FLAGGED,
        EmailFetchingCriterionChoices.UNFLAGGED,
        EmailFetchingCriterionChoices.DRAFT,
        EmailFetchingCriterionChoices.UNDRAFT,
        EmailFetchingCriterionChoices.ANSWERED,
        EmailFetchingCriterionChoices.UNANSWERED,
        EmailFetchingCriterionChoices.DELETED,
        EmailFetchingCriterionChoices.UNDELETED,
        EmailFetchingCriterionChoices.DAILY,
        EmailFetchingCriterionChoices.WEEKLY,
        EmailFetchingCriterionChoices.MONTHLY,
        EmailFetchingCriterionChoices.ANNUALLY,
        EmailFetchingCriterionChoices.SENTSINCE,
        EmailFetchingCriterionChoices.SUBJECT,
        EmailFetchingCriterionChoices.BODY,
        EmailFetchingCriterionChoices.FROM,
        EmailFetchingCriterionChoices.KEYWORD,
        EmailFetchingCriterionChoices.UNKEYWORD,
        EmailFetchingCriterionChoices.LARGER,
        EmailFetchingCriterionChoices.SMALLER,
    )
    """Tuple of all criteria available for fetching. Refers to :class:`MailFetchingCriteria`.
    Must be immutable!
    IMAP4 does not accept time lookups, only date based.
    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4.
    """

    EMAIL_FETCH_BATCH_SIZE = 100

    @override
    def __init__(self, account: Account) -> None:
        """Constructor, starts the IMAP connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        super().__init__(account)

        self.connect_to_host()
        self.safe_login(  # dont use kwargs here, this would kill the utf-8 fallback!
            self.account.mail_address, self.account.password
        )

    @override
    def connect_to_host(self) -> None:
        """Opens the connection to the IMAP server using the credentials from :attr:`account`.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Connecting to %s ...", self.account)

        mail_host = self.account.mail_host
        mail_host_port = self.account.mail_host_port
        timeout = self.account.timeout
        try:
            if mail_host_port:
                self._mail_client = imaplib.IMAP4(
                    host=mail_host, port=mail_host_port, timeout=timeout
                )
            else:
                self._mail_client = imaplib.IMAP4(host=mail_host, timeout=timeout)
        except Exception as error:
            self.logger.exception("Error connecting to %s!", self.account)
            raise MailAccountError(error, _("connecting")) from error
        self.logger.info("Successfully connected to %s.", self.account)

    @override
    def test(self, mailbox: Mailbox | None = None) -> None:
        """Tests the connection to the mailserver and, if a mailbox is provided, whether it can be opened and listed.

        Args:
            mailbox: The mailbox to be tested. Default is None.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
            MailAccountError: If the account test fails because an error occurs or a bad response is returned.
            MailboxError: If the mailbox test fails because an error occurs or a bad response is returned testing the mailbox.
        """
        super().test(mailbox)

        self.logger.debug("Testing %s ...", self.account)
        self.safe_noop()
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            self.logger.debug("Testing %s ...", mailbox)
            self.safe_select(utf7_encode(mailbox.name), readonly=True)
            self.safe_check()
            self.safe_unselect()
            self.logger.debug("Successfully tested %s.", mailbox)

    @override
    def fetch_emails(
        self,
        mailbox: Mailbox,
        criterion: FetchingCriterion = BaseFetcher.DEFAULT_FETCHING_CRITERION,
    ) -> list[bytes]:
        """Fetches and returns maildata from a mailbox based on a given criterion.

        Todo:
            Rewrite this into a generator.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails in the IMAP request.
                Defaults to :attr:`eonvelope.MailFetchingCriteria.ALL`.

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
                If :attr:`criterion` is not in :attr:`IMAP4Fetcher.AVAILABLE_FETCHING_CRITERIA`.
            MailboxError: If an error occurs or a bad response is returned during an action on the mailbox.
        """
        super().fetch_emails(mailbox, criterion)

        search_criterion = criterion.as_imap_criterion()

        self.logger.debug(
            "Searching and fetching %s messages in %s...",
            search_criterion,
            mailbox,
        )
        self.logger.debug("Opening mailbox %s ...", mailbox)
        self.safe_select(utf7_encode(mailbox.name), readonly=True)
        self.logger.debug("Successfully opened mailbox.")

        self.logger.debug("Searching %s messages in %s ...", search_criterion, mailbox)
        if "SORT" in self._mail_client.capabilities:
            _, message_uids = self.safe_uid("SORT", "(DATE)", "UTF-8", search_criterion)
        else:
            _, message_uids = self.safe_uid("SEARCH", search_criterion)
        self.logger.info(
            "Found %s messages with uIDs %s in %s.",
            search_criterion,
            message_uids,
            mailbox,
        )

        self.logger.debug("Fetching %s messages in %s ...", search_criterion, mailbox)
        mail_data_list = []
        message_uid_list = message_uids[0].split()
        for uids in batched(
            message_uid_list, self.EMAIL_FETCH_BATCH_SIZE, strict=False
        ):
            try:
                _, message_data = self.safe_uid("FETCH", b",".join(uids), "(RFC822)")
            except FetcherError:
                self.logger.warning(
                    "Failed to fetch messages %s from %s!",
                    uids,
                    mailbox,
                    exc_info=True,
                )
                continue
            mail_data_list.extend([message for _, message in message_data[::2]])
        self.logger.debug(
            "Successfully fetched %s messages from %s.",
            search_criterion,
            mailbox,
        )

        self.logger.debug("Leaving mailbox %s ...", mailbox)
        self.safe_unselect()
        self.logger.debug("Successfully left mailbox.")

        self.logger.debug(
            "Successfully searched and fetched %s messages in %s.",
            search_criterion,
            mailbox,
        )

        return mail_data_list

    @override
    def fetch_mailboxes(self) -> list[tuple[str, str]]:
        """Retrieves and returns the data of the mailboxes in the account.

        Todo:
            Rewrite this into a generator.

        Returns:
            List of data of all mailboxes in the account. Empty if none are found.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Fetching mailboxes in %s ...", self.account)
        _, mailboxes_data = self.safe_list()
        mailboxes = [
            parse_IMAP_mailbox_data(mailbox_data)
            for mailbox_data in mailboxes_data
            if isinstance(mailbox_data, bytes | str)
        ]
        self.logger.debug("Successfully fetched mailboxes in %s.", self.account)
        return mailboxes

    @override
    def restore(self, email: Email) -> None:
        """Places an email in its mailbox.

        Args:
            email: The email to restore.

        Raises:
            ValueError: If the emails mailbox is not in this fetchers account.
            FileNotFoundError: If the email has no eml file in storage.
            MailboxError: If uploading the email to the mailserver fails or returns a bad response.
        """
        super().restore(email)
        self.logger.debug("Restoring %s to its mailbox ...", email)
        with email.open_file() as email_file:
            self.safe_append(email.mailbox.name, None, None, email_file.read())
        self.logger.debug("Successfully restored email.")

    @override
    def close(self) -> None:
        """Logs out of the account and closes the connection to the IMAP server if it is open."""
        self.logger.debug("Closing connection to %s ...", self.account)
        self.safe_logout()
        self.logger.info("Successfully closed connection to %s.", self.account)
