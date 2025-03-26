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

"""Module with the :class:`AccountModel` model class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Final

import django.db
from dirtyfields import DirtyFieldsMixin
from django.contrib.auth.models import User
from django.db import models

from core.constants import EmailProtocolChoices

from ..utils.fetchers.exceptions import MailAccountError
from ..utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from ..utils.fetchers.IMAPFetcher import IMAPFetcher
from ..utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from ..utils.fetchers.POP3Fetcher import POP3Fetcher
from .MailboxModel import MailboxModel


# from utils.fetchers.ExchangeFetcher import ExchangeFetcher
if TYPE_CHECKING:
    from ..utils.fetchers.BaseFetcher import BaseFetcher


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class AccountModel(DirtyFieldsMixin, models.Model):
    """Database model for the account data of a mail account."""

    mail_address = models.EmailField(
        max_length=255,
        verbose_name="Email address",
        help_text="The mail address to the account.",
    )
    """The mail address of the account. Unique together with :attr:`user`."""

    password = models.CharField(max_length=255, verbose_name="Password")
    """The password to log into the account."""

    mail_host = models.CharField(
        max_length=255,
        verbose_name="Mailserver-URL",
        help_text="The URL of the mailserver for the chosen protocol.",
    )
    """The url of the mail server where the account is located."""

    mail_host_port = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Mailserver-Port",
        help_text="The port of the mailserver for the chosen protocol.",
    )
    """The port of the mail server. Can be null if the default port of the protocol is used."""

    protocol = models.CharField(
        choices=EmailProtocolChoices.choices,
        max_length=10,
        verbose_name="Email Protocol",
        help_text="The email protocol implemented by the server.",
    )
    """The mail protocol of the mail server."""

    timeout = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Connection Timeout",
        help_text="Timeout for the connection to the mailserver.",
    )
    """The timeout parameter for the connection to the host. Can be null."""

    is_healthy = models.BooleanField(default=True)
    """Flags whether the account can be accessed using the data. True by default.
    When this field changes to `False`, all mailboxes :attr:`core.models.MailboxModel.is_healthy` field will be updated accordingly.
    When the :attr:`core.models.MailboxModel.is_healthy` field of one of the mailboxes referencing this entry via :attr:`core.models.MailboxModel.account`
    becomes `True` after being `False`, this field will be set to `True` as well."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite accounts. False by default."""

    user = models.ForeignKey(User, related_name="accounts", on_delete=models.CASCADE)
    """The user this account belongs to. Deletion of that `user` deletes this correspondent."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    class Meta:
        """Metadata class for the model."""

        db_table = "accounts"
        """The name of the database table for the mail accounts."""

        constraints: Final[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["mail_address", "user"],
                name="account_unique_together_mail_address_user",
            ),
            models.CheckConstraint(
                condition=models.Q(protocol__in=EmailProtocolChoices.values),
                name="protocol_valid_choice",
            ),
        ]
        """`mail_address` and :attr:`user` in combination are unique fields.
        Choices for :attr:`protocol` are enforced on db level.
        """

    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the account, using :attr:`mail_address`, :attr:`mail_host` and :attr:`protocol`.
        """
        return f"Account {self.mail_address} with protocol {self.protocol}"

    def get_fetcher_class(self) -> type[BaseFetcher]:
        """Returns the fetcher class from :class:`core.utils.fetchers` corresponding to :attr:`protocol`.

        Returns:
            The fetcher class for the account.

        Raises:
            ValueError: If the protocol doesnt match any fetcher class.
                Marks the account as unhealthy in this case.
        """
        if self.protocol == IMAPFetcher.PROTOCOL:
            return IMAPFetcher
        if self.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            return IMAP_SSL_Fetcher
        if self.protocol == POP3Fetcher.PROTOCOL:
            return POP3Fetcher
        if self.protocol == POP3_SSL_Fetcher.PROTOCOL:
            return POP3_SSL_Fetcher
        # if self.protocol == ExchangeFetcher.PROTOCOL:
        #     return ExchangeFetcher

        logger.error(
            "The protocol %s is not implemented in a fetcher class!", self.protocol
        )
        self.is_healthy = False
        self.save(update_fields=["is_healthy"])
        raise ValueError(
            "The requested protocol is not implemented in a fetcher class!"
        )

    def get_fetcher(self) -> BaseFetcher:
        """Convenience method: Instantiates the fetcher from :class:`core.utils.fetchers` corresponding to :attr:`protocol`.

        Returns:
            A fetcher instance for the account.

        Raises:
            ValueError: If the protocol doesnt match any fetcher class.
                Marks the account as unhealthy in this case.
        """
        return self.get_fetcher_class()(self)

    def test_connection(self) -> None:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.AccountModel.is_healthy` flag is set accordingly.
        Relies on the `test` method of the :mod:`core.utils.fetchers` classes.

        Raises:
            MailAccountError: If the test is fails.
        """
        logger.info("Testing %s ...", self)
        try:
            with self.get_fetcher() as fetcher:
                fetcher.test()
        except MailAccountError as error:
            logger.info("Testing %s failed with error: %s.", self, error)
            self.is_healthy = False
            self.save(update_fields=["is_healthy"])
            raise
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])
        logger.info("Successfully tested account.")

    def update_mailboxes(self) -> None:
        """Scans the given mailaccount for unknown mailboxes, parses and inserts them into the database.

        If successful, marks this account as healthy, otherwise unhealthy.

        Raises:
            MailAccountError: If scanning for mailboxes failed.
        """

        logger.info("Updating mailboxes in %s...", self)
        try:
            with self.get_fetcher() as fetcher:
                mailboxList = fetcher.fetchMailboxes()
        except MailAccountError:
            self.is_healthy = False
            self.save(update_fields=["is_healthy"])
            raise
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])

        for mailboxData in mailboxList:
            mailbox = MailboxModel.fromData(mailboxData, self)

            logger.debug("Saving mailbox %s from %s to db ...", mailbox, self)
            try:
                mailbox.save()
                logger.debug("Successfully saved mailbox to db!")
            except django.db.IntegrityError:
                logger.debug("%s already exists in db, it is skipped!", mailbox)

        logger.info("Successfully updated mailboxes.")
