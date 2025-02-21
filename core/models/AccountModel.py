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

from core import constants

from ..constants import TestStatusCodes
from ..utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from ..utils.fetchers.IMAPFetcher import IMAPFetcher
from ..utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from ..utils.fetchers.POP3Fetcher import POP3Fetcher
from .MailboxModel import MailboxModel


# from utils.fetchers.ExchangeFetcher import ExchangeFetcher
if TYPE_CHECKING:
    from imaplib import IMAP4
    from poplib import POP3


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class AccountModel(DirtyFieldsMixin, models.Model):
    """Database model for the account data of a mail account."""

    mail_address = models.EmailField(max_length=255)
    """The mail address of the account. Unique together with :attr:`user`."""

    password = models.CharField(max_length=255)
    """The password to log into the account."""

    mail_host = models.CharField(max_length=255)
    """The url of the mail server where the account is located."""

    mail_host_port = models.IntegerField(null=True)
    """The port of the mail server. Can be null if the default port of the protocol is used."""

    PROTOCOL_CHOICES: Final[list[tuple[str, str]]] = list(
        constants.MailFetchingProtocols()
    )
    """The available mail protocols."""

    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=10)
    """The mail protocol of the mail server. One of :attr:`PROTOCOL_CHOICES`."""

    timeout = models.IntegerField(null=True)
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
            )
        ]
        """`mail_address` and :attr:`user` in combination are unique fields."""

    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the account, using :attr:`mail_address`, :attr:`mail_host` and :attr:`protocol`.
        """
        return f"Account {self.mail_address} at host {self.mail_host} with protocol {self.protocol}"

    def get_fetcher(self) -> IMAP4 | POP3:
        """Instantiates the fetcher from :class:`core.utils.fetchers` corresponding to :attr:`protocol`.

        Returns:
            A fetcher instance for the account.

        Raises:
            ValueError: If the protocol doesnt match any fetcher class.
                Marks the account as unhealthy in this case.
        """

        if self.protocol == IMAPFetcher.PROTOCOL:
            return IMAPFetcher(self)
        if self.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            return IMAP_SSL_Fetcher(self)
        if self.protocol == POP3Fetcher.PROTOCOL:
            return POP3Fetcher(self)
        if self.protocol == POP3_SSL_Fetcher.PROTOCOL:
            return POP3_SSL_Fetcher(self)
        # if self.protocol == ExchangeFetcher.PROTOCOL:
        #     return ExchangeFetcher(self)

        logger.error(
            "The protocol %s is not implemented in a fetcher class!", self.protocol
        )
        self.is_healthy = False
        self.save(update_fields=["is_healthy"])
        raise ValueError(
            "The requested protocol is not implemented in a fetcher class!"
        )

    def test_connection(self) -> int:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.AccountModel.is_healthy` flag is set accordingly.
        Relies on the `test` method of the :mod:`core.utils.fetchers` classes.

        Returns:
            The resultcode of the test.
        """
        logger.info("Testing %s ...", self)
        try:
            with self.get_fetcher() as fetcher:
                result = fetcher.test()
        except ValueError:
            logger.exception("Account %s has unknown protocol!", self)
            result = TestStatusCodes.ERROR

        logger.info("Successfully tested account to be %s.", result)
        return result

    def update_mailboxes(self) -> None:
        """Scans the given mailaccount for unknown mailboxes, parses and inserts them into the database."""

        logger.info("Updating mailboxes in %s...", self)

        with self.get_fetcher() as fetcher:
            mailboxList = fetcher.fetchMailboxes()

        for mailboxData in mailboxList:
            mailbox = MailboxModel.fromData(mailboxData, self)

            logger.debug("Saving mailbox %s from %s to db ...", mailbox, self)
            try:
                mailbox.save()
                logger.debug("Successfully saved mailbox to db!")
            except django.db.IntegrityError:
                logger.debug("%s already exists in db, it is skipped!", mailbox)

        logger.info("Successfully updated mailboxes.")
