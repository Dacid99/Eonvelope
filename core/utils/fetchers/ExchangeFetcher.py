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

"""Module with the :class:`ExchangeFetcher` class."""

from __future__ import annotations

import datetime
import os
from typing import TYPE_CHECKING, Final, override

import exchangelib
import exchangelib.errors
from django.utils import timezone

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.utils.fetchers.exceptions import MailAccountError, MailboxError

from .BaseFetcher import BaseFetcher


if TYPE_CHECKING:
    from exchangelib.queryset import QuerySet

    from ...models.Account import Account
    from ...models.Mailbox import Mailbox


class ExchangeFetcher(BaseFetcher):
    """Maintains a connection to the Exchange server and fetches data using :mod:`imaplib`.

    Opens a connection to the Exchange server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an Exchange host.
    """

    PROTOCOL = EmailProtocolChoices.EXCHANGE.value
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.Exchange`."""

    AVAILABLE_FETCHING_CRITERIA: Final[list[str]] = [
        EmailFetchingCriterionChoices.ALL.value,
        EmailFetchingCriterionChoices.SEEN.value,
        EmailFetchingCriterionChoices.UNSEEN.value,
        EmailFetchingCriterionChoices.DRAFT.value,
        EmailFetchingCriterionChoices.DAILY.value,
        EmailFetchingCriterionChoices.WEEKLY.value,
        EmailFetchingCriterionChoices.MONTHLY.value,
        EmailFetchingCriterionChoices.ANNUALLY.value,
    ]
    """List of all criteria available for fetching. Refers to :class:`EmailFetchingCriterionChoices`.
    Constructed analogous to the IMAP4 criteria.
    """

    def make_fetching_query(self, criterion: str, base_query: QuerySet) -> QuerySet:
        """Returns the queryset for the Exchange request.

        Args:
            criterion_name: The criterion for the Exchange request.

        Returns:
            Augmented queryset to be used in Exchange request.
        """
        if criterion == EmailFetchingCriterionChoices.UNSEEN:
            mail_query = base_query.filter(is_read=False)
        elif criterion == EmailFetchingCriterionChoices.SEEN:
            mail_query = base_query.filter(is_read=True)
        elif criterion == EmailFetchingCriterionChoices.DRAFT:
            mail_query = base_query.filter(is_draft=True)
        elif criterion == EmailFetchingCriterionChoices.DAILY:
            start_time = timezone.now() - datetime.timedelta(days=1)
            mail_query = base_query.filter(datetime_received__gte=start_time)
        elif criterion == EmailFetchingCriterionChoices.WEEKLY:
            start_time = timezone.now() - datetime.timedelta(weeks=1)
            mail_query = base_query.filter(datetime_received__gte=start_time)
        elif criterion == EmailFetchingCriterionChoices.MONTHLY:
            start_time = timezone.now() - datetime.timedelta(weeks=4)
            mail_query = base_query.filter(datetime_received__gte=start_time)
        elif criterion == EmailFetchingCriterionChoices.ANNUALLY:
            start_time = timezone.now() - datetime.timedelta(weeks=52)
            mail_query = base_query.filter(datetime_received__gte=start_time)
        else:
            mail_query = base_query
        return mail_query

    @override
    def __init__(self, account: Account) -> None:
        """Constructor, starts the Exchange connection and logs into the account.

        Args:
            account: The model of the account to be fetched from.
        """
        super().__init__(account)

        self.connect_to_host()

    @override
    def connect_to_host(self) -> None:
        """Opens the connection to the Exchange server using the credentials from :attr:`account`.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """

        credentials = exchangelib.Credentials(
            self.account.mail_address, self.account.password
        )
        config = exchangelib.Configuration(
            server=self.account.mail_host, credentials=credentials
        )
        self._mail_client = exchangelib.Account(
            primary_smtp_address=self.account.mail_address,
            config=config,
            access_type=exchangelib.DELEGATE,
            autodiscover=False,
            default_timezone=exchangelib.EWSTimeZone(
                "UTC"
            ),  # for consistency with celery and django settings
        )

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
        try:
            self._mail_client.root.refresh()
        except exchangelib.errors.EWSError as exc:
            raise MailAccountError from exc
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            self.logger.debug("Testing %s ...", mailbox)
            try:
                (self._mail_client.inbox.parent / mailbox.name).refresh()
            except exchangelib.errors.EWSError as exc:
                raise MailboxError from exc
            self.logger.debug("Successfully tested %s.", mailbox)

    @override
    def fetch_emails(
        self,
        mailbox: Mailbox,
        criterion: str = EmailFetchingCriterionChoices.ALL,
    ) -> list[bytes]:
        """Fetches and returns maildata from a mailbox based on a given criterion.

        Todo:
            Rewrite this into a generator.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails in the Exchange server.
                Defaults to :attr:`Emailkasten.MailFetchingCriteria.ALL`.

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
                If :attr:`criterion` is not in :attr:`ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA`.
            MailboxError: If an error occurs or a bad response is returned.
        """
        super().fetch_emails(mailbox, criterion)
        try:
            mail_root = self._mail_client.inbox.parent
            base_mail_query = (mail_root / mailbox.name).all()
            mail_query = self.make_fetching_query(criterion, base_mail_query)
            mail_data_list = [mail.mime_content for mail in mail_query]
        except exchangelib.errors.EWSError as error:
            raise MailboxError from error
        return mail_data_list

    @override
    def fetch_mailboxes(self) -> list[str]:
        """Retrieves and returns the data of the mailboxes in the account.

        Todo:
            Rewrite this into a generator.

        Note:
            Considers only children of the parent of the inbox.

        Returns:
            List of paths of all mailboxes in the account relative to the parent folder of the inbox.
            Empty if none are found.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Fetching mailboxes at %s ...", self.account)
        try:
            mail_root = self._mail_client.inbox.parent
            mail_root_path = mail_root.absolute
            mailbox_names = [
                os.path.relpath(folder.absolute, mail_root_path)
                for folder in mail_root.walk()
                if isinstance(folder, exchangelib.Folder)
                and folder.folder_class == "IPF.Note"
            ]
        except exchangelib.errors.EWSError as error:
            raise MailAccountError from error
        return mailbox_names

    @override
    def close(self) -> None:
        """Not required for Exchangelib."""
