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

"""Module with the :class:`ExchangeFetcher` class."""

from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, override

import exchangelib
import exchangelib.errors
from django.utils.translation import gettext as _

from core.constants import (
    INTERNAL_DATE_FORMAT,
    EmailFetchingCriterionChoices,
    EmailProtocolChoices,
)
from core.utils.fetchers.exceptions import MailAccountError, MailboxError

from .BaseFetcher import BaseFetcher


if TYPE_CHECKING:
    from exchangelib.queryset import QuerySet

    from core.models.Account import Account
    from core.models.Email import Email
    from core.models.Mailbox import Mailbox


class ExchangeFetcher(BaseFetcher):
    """Maintains a connection to the Exchange server and fetches data using :mod:`imaplib`.

    Opens a connection to the Exchange server on construction and is preferably used in a 'with' environment.
    Allows fetching of mails and mailboxes from an account on an Exchange host.
    """

    PROTOCOL = EmailProtocolChoices.EXCHANGE
    """Name of the used protocol, refers to :attr:`MailFetchingProtocols.Exchange`."""

    AVAILABLE_FETCHING_CRITERIA = (
        EmailFetchingCriterionChoices.ALL,
        EmailFetchingCriterionChoices.SEEN,
        EmailFetchingCriterionChoices.UNSEEN,
        EmailFetchingCriterionChoices.DRAFT,
        EmailFetchingCriterionChoices.UNDRAFT,
        EmailFetchingCriterionChoices.DAILY,
        EmailFetchingCriterionChoices.WEEKLY,
        EmailFetchingCriterionChoices.MONTHLY,
        EmailFetchingCriterionChoices.ANNUALLY,
        EmailFetchingCriterionChoices.SUBJECT,
        EmailFetchingCriterionChoices.BODY,
    )
    """Tuple of all criteria available for fetching. Refers to :class:`EmailFetchingCriterionChoices`.
    Constructed analogous to the IMAP4 criteria.
    Must be immutable!
    """

    @staticmethod
    def make_fetching_query(
        criterion: str, criterion_arg: str, base_query: QuerySet
    ) -> QuerySet:
        """Returns the queryset for the Exchange request.

        Note:
            Use no timezone here to use the mailserver time settings.

        Args:
            criterion: The criterion for the Exchange request.
            criterion_arg: The argument for the criterion.
            base_query: The query to extend based on the criterion.

        Returns:
            Augmented queryset to be used in Exchange request.
        """
        match criterion:
            case EmailFetchingCriterionChoices.DAILY:
                start_time = datetime.now(tz=UTC) - timedelta(days=1)
            case EmailFetchingCriterionChoices.WEEKLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=1)
            case EmailFetchingCriterionChoices.MONTHLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=4)
            case EmailFetchingCriterionChoices.ANNUALLY:
                start_time = datetime.now(tz=UTC) - timedelta(weeks=52)
            case EmailFetchingCriterionChoices.SENTSINCE:
                start_time = datetime.strptime(
                    criterion_arg, INTERNAL_DATE_FORMAT
                ).astimezone(UTC)
            case EmailFetchingCriterionChoices.SUBJECT:
                return base_query.filter(subject__contains=criterion_arg)
            case EmailFetchingCriterionChoices.BODY:
                return base_query.filter(body__contains=criterion_arg)
            case EmailFetchingCriterionChoices.UNSEEN:
                return base_query.filter(is_read=False)
            case EmailFetchingCriterionChoices.SEEN:
                return base_query.filter(is_read=True)
            case EmailFetchingCriterionChoices.DRAFT:
                return base_query.filter(is_draft=True)
            case EmailFetchingCriterionChoices.UNDRAFT:
                return base_query.filter(is_draft=False)
            case _:  # only ALL left
                return base_query
        return base_query.filter(datetime_received__gte=start_time)

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
            MailAccountError: If an error occurs accessing the msg_folder_root.
        """

        self.logger.debug("Setting up connection to %s ...", self.account)
        credentials = exchangelib.Credentials(
            self.account.mail_address, self.account.password
        )
        retry_policy = exchangelib.FaultTolerance(max_wait=self.account.timeout)
        config = (
            exchangelib.Configuration(
                service_endpoint=self.account.mail_host,
                credentials=credentials,
                retry_policy=retry_policy,
            )
            if self.account.mail_host.startswith("http://")
            or self.account.mail_host.startswith("https://")
            else exchangelib.Configuration(
                server=self.account.mail_host_address,
                credentials=credentials,
                retry_policy=retry_policy,
            )
        )
        exchange_account = exchangelib.Account(
            primary_smtp_address=self.account.mail_address,
            config=config,
            access_type=exchangelib.DELEGATE,
            autodiscover=False,
            default_timezone=exchangelib.EWSTimeZone(
                "UTC"
            ),  # for consistency with celery and django settings
        )
        try:
            self._mail_client = exchange_account.msg_folder_root
        except exchangelib.errors.EWSError as error:
            self.logger.exception(
                "Error connecting to %s!",
                self.account,
            )
            raise MailAccountError(error, "connecting") from error
        self.logger.info("Successfully set up connection to %s.", self.account)

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
            self._mail_client.refresh()
        except exchangelib.errors.EWSError as error:
            self.logger.exception("Error during refresh of message_root!")
            raise MailAccountError(error, _("refresh")) from error
        self.logger.debug("Successfully tested %s.", self.account)

        if mailbox is not None:
            self.logger.debug("Testing %s ...", mailbox)
            try:
                self.open_mailbox(mailbox).refresh()
            except exchangelib.errors.EWSError as error:
                self.logger.exception(
                    "Error during refresh of %s!",
                    mailbox.name,
                )
                raise MailboxError(error, _("refresh")) from error
            self.logger.debug("Successfully tested %s.", mailbox)

    @override
    def fetch_emails(
        self,
        mailbox: Mailbox,
        criterion: str = EmailFetchingCriterionChoices.ALL,
        criterion_arg: str = "",
    ) -> list[bytes]:
        """Fetches and returns maildata from a mailbox based on a given criterion.

        Todo:
            Rewrite this into a generator.

        Args:
            mailbox: Database model of the mailbox to fetch data from.
            criterion: Formatted criterion to filter mails in the Exchange server.
                Defaults to :attr:`eonvelope.MailFetchingCriteria.ALL`.
            criterion_arg: The argument for the criterion.
                Defaults to "".

        Returns:
            List of mails in the mailbox matching the criterion as :class:`bytes`.
            Empty if no such messages are found.

        Raises:
            ValueError: If the :attr:`mailbox` does not belong to :attr:`self.account`.
                If :attr:`criterion` is not in :attr:`ExchangeFetcher.AVAILABLE_FETCHING_CRITERIA`.
            MailboxError: If an error occurs or a bad response is returned during an action on the mailbox..
        """
        super().fetch_emails(mailbox, criterion, criterion_arg)
        self.logger.debug(
            "Searching and fetching %s messages in %s...",
            criterion.format(criterion_arg),
            mailbox,
        )
        try:
            mailbox_folder = self.open_mailbox(mailbox)
            mail_query = self.make_fetching_query(
                criterion,
                criterion_arg,
                mailbox_folder.all().order_by("datetime_received"),
            )
            mail_data_list = [mail.mime_content for mail in mail_query]
        except exchangelib.errors.EWSError as error:
            self.logger.exception("Error during fetching of mail contents!")
            raise MailboxError(error, _("fetching of mail contents")) from error
        self.logger.info(
            "Successfully searched and fetched %s %s messages in %s.",
            len(mail_data_list),
            criterion,
            mailbox,
        )
        return mail_data_list

    @override
    def fetch_mailboxes(self) -> list[str]:
        """Retrieves and returns the data of the mailboxes in the account.

        Todo:
            Rewrite this into a generator.

        Note:
            Considers only children of the msg_folder_root.

        Returns:
            List of paths of all mailboxes in the account relative to the parent folder of the inbox.
            Empty if none are found.

        Raises:
            MailAccountError: If an error occurs or a bad response is returned.
        """
        self.logger.debug("Fetching mailboxes in %s ...", self.account)
        try:
            mail_root_path = self._mail_client.absolute
            mailbox_names = [
                os.path.relpath(folder.absolute, mail_root_path)
                for folder in self._mail_client.walk()
                if isinstance(folder, exchangelib.Folder)
                and folder.folder_class == "IPF.Note"
            ]
        except exchangelib.errors.EWSError as error:
            self.logger.exception("Error during scan of message_root!")
            raise MailAccountError(error, _("scan for mailboxes")) from error
        self.logger.debug("Successfully fetched mailboxes in %s.", self.account)
        return mailbox_names

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
        self.logger.debug("Restoring email %s to its mailbox ...", email)
        with email.open_file() as email_file:
            try:
                exchangelib.Message(
                    folder=self.open_mailbox(email.mailbox),
                    mime_content=email_file.read(),
                ).save()
            except exchangelib.errors.EWSError as error:
                self.logger.exception("Error during restoring of email!")
                raise MailboxError(error, _("restoring of email")) from error
        self.logger.debug("Successfully restored email.")

    @override
    def close(self) -> None:
        """No cleanup of :class:`exchangelib.Account` required."""

    def open_mailbox(self, mailbox: Mailbox) -> exchangelib.Folder:
        """Helper method to correctly open a mailbox folder.

        Note:
            This may cause problems with mailboxes that have / in their name (should be very uncommon).

        Returns:
            The mailbox folder instance.
        """
        mailbox_folder = self._mail_client
        for folder_name in mailbox.name.split("/"):
            mailbox_folder = mailbox_folder / folder_name
        return mailbox_folder
