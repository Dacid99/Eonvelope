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

"""Module with the :class:`Account` model class."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar, override

from dirtyfields import DirtyFieldsMixin
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_prometheus.models import ExportModelOperationsMixin

from core.constants import EmailProtocolChoices
from core.mixins import (
    FavoriteModelMixin,
    HealthModelMixin,
    TimestampModelMixin,
    URLMixin,
)
from core.utils.fetchers import (
    ExchangeFetcher,
    IMAP4_SSL_Fetcher,
    IMAP4Fetcher,
    POP3_SSL_Fetcher,
    POP3Fetcher,
)
from core.utils.fetchers.exceptions import MailAccountError

from .Mailbox import Mailbox


if TYPE_CHECKING:
    from core.utils.fetchers import BaseFetcher


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Account(
    ExportModelOperationsMixin("account"),
    DirtyFieldsMixin,
    URLMixin,
    FavoriteModelMixin,
    TimestampModelMixin,
    HealthModelMixin,
    models.Model,
):
    """Database model for the account data of a mail account."""

    BASENAME = "account"

    DELETE_NOTICE = _(
        "This will delete the records of this account and all mailboxes, emails and attachments found in it!"
    )
    DELETE_NOTICE_PLURAL = _(
        "This will delete the records of these accounts and all mailboxes, emails and attachments found in them!"
    )

    MAX_MAIL_HOST_PORT = 65535

    mail_address = models.EmailField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("email address"),
        help_text=_("The mail address to the account."),
    )
    """The mail address of the account. Unique together with :attr:`user`."""

    password = models.CharField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("password"),
        help_text=_("The password to the account."),
    )
    """The password to log into the account."""

    mail_host = models.CharField(
        max_length=255,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("mailserver URL"),
        help_text=_("The URL of the mailserver for the chosen protocol."),
    )
    """The url of the mail server where the account is located."""

    mail_host_port = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(MAX_MAIL_HOST_PORT)],
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("mailserver portnumber"),
        help_text=_("The port of the mailserver for the chosen protocol."),
    )
    """The port of the mail server. Can be null if the default port of the protocol is used."""

    protocol = models.CharField(
        choices=EmailProtocolChoices.choices,
        max_length=10,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("email protocol"),
        help_text=_("The email protocol implemented by the server."),
    )
    """The mail protocol of the mail server."""

    timeout = models.PositiveIntegerField(
        default=10,
        blank=True,
        validators=[MinValueValidator(0.1)],
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("connection timeout"),
        help_text=_("Timeout for the connection to the mailserver."),
    )
    """The timeout parameter for the connection to the host, defaults to 10s."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="accounts",
        on_delete=models.CASCADE,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("user"),
    )
    """The user this account belongs to. Deletion of that `user` deletes this correspondent."""

    class Meta:
        """Metadata class for the model."""

        db_table = "accounts"
        """The name of the database table for the mail accounts."""
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name = _("account")
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name_plural = _("accounts")
        get_latest_by = TimestampModelMixin.Meta.get_latest_by

        constraints: ClassVar[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["mail_address", "protocol", "user"],
                name="account_unique_together_mail_address_protocol_user",
            ),
            models.CheckConstraint(
                condition=models.Q(protocol__in=EmailProtocolChoices.values),
                name="protocol_valid_choice",
            ),
        ]
        """`mail_address` and :attr:`user` in combination are unique fields.
        Choices for :attr:`protocol` are enforced on db level.
        """

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the account, using :attr:`mail_address` and :attr:`protocol`.
        """
        return _("Account %(mail_address)s with protocol %(protocol)s") % {
            "mail_address": self.mail_address,
            "protocol": self.protocol,
        }

    @override
    def clean(self) -> None:
        """Validation for the unique together constraint on :attr:`mail_account`.
        Validate the account data by testing if one of the relevant fields is dirty.

        Required to allow correct validation of the create form.

        Raises:
            ValidationError: If the instance violates the constraint or testing fails.
        """
        if (
            Account.objects.filter(
                user=self.user, mail_address=self.mail_address, protocol=self.protocol
            )
            .exclude(pk=self.pk)
            .exists()
        ):
            raise ValidationError({"mail_address": _("This account already exists.")})

        test_on_dirty_fields = [
            "mail_address",
            "password",
            "mail_host",
            "mail_host_port",
            "protocol",
        ]
        dirty_fields = self.get_dirty_fields()
        if any(field in dirty_fields for field in test_on_dirty_fields):
            try:
                self.test()
            except MailAccountError as error:
                raise ValidationError(
                    _("Testing this account data failed: %(error)s")
                    % {"error": str(error)}
                ) from error

    def get_fetcher_class(self) -> type[BaseFetcher]:
        """Returns the fetcher class from :class:`core.utils.fetchers` corresponding to :attr:`protocol`.

        Returns:
            The fetcher class for the account.

        Raises:
            ValueError: If the protocol doesn't match any fetcher class.
                Marks the account as unhealthy in this case.
        """
        if self.protocol == IMAP4Fetcher.PROTOCOL:
            return IMAP4Fetcher
        if self.protocol == IMAP4_SSL_Fetcher.PROTOCOL:
            return IMAP4_SSL_Fetcher
        if self.protocol == POP3Fetcher.PROTOCOL:
            return POP3Fetcher
        if self.protocol == POP3_SSL_Fetcher.PROTOCOL:
            return POP3_SSL_Fetcher
        if self.protocol == ExchangeFetcher.PROTOCOL:
            return ExchangeFetcher

        logger.error(
            "The protocol %s is not implemented in a fetcher class!", self.protocol
        )
        self.set_unhealthy(
            _("The protocol %s is not implemented in a fetcher class!") % self.protocol
        )
        raise ValueError(
            _("The protocol %s is not implemented in a fetcher class!") % self.protocol
        )

    def get_fetcher(self) -> BaseFetcher:
        """Instantiates the fetcher from :class:`core.utils.fetchers` corresponding to :attr:`protocol`.

        Handles possible errors instantiating the fetcher.

        Returns:
            A fetcher instance for the account.

        Raises:
            ValueError: If the protocol doesn't match any fetcher class.
                Marks the account as unhealthy in this case.
            MailAccountError: If the fetcher fails to initialize.
                Marks the account as unhealthy in this case.
        """
        try:
            fetcher = self.get_fetcher_class()(self)
        except MailAccountError as error:
            logger.exception("Failed to instantiate fetcher for %s!", self)
            self.set_unhealthy(error)
            raise
        return fetcher

    def test(self) -> None:
        """Tests whether the data in the model is correct.

        Tests connecting and logging in to the mailhost and account.
        The :attr:`core.models.Account.is_healthy` flag is set accordingly.
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
            self.set_unhealthy(error)
            raise
        self.set_healthy()
        logger.info("Successfully tested account.")

    def update_mailboxes(self) -> None:
        """Scans the given mailaccount for unknown mailboxes, parses and inserts them into the database.

        If successful, marks this account as healthy, otherwise unhealthy.

        Raises:
            MailAccountError: If scanning for mailboxes failed.
        """

        logger.info("Updating mailboxes in %s...", self)
        with self.get_fetcher() as fetcher:
            try:
                mailbox_list = fetcher.fetch_mailboxes()
            except MailAccountError as error:
                self.set_unhealthy(error)
                raise
        self.set_healthy()

        logger.info("Parsing mailbox data ...")

        for mailbox_data in mailbox_list:
            Mailbox.create_from_data(mailbox_data, self)

        logger.info("Successfully updated mailboxes.")

    @property
    def mail_host_address(self) -> str:
        """The mail_host address with port specified for the hostname.

        Returns:
            The complete host address.
        """
        return (
            f"{self.mail_host}:{self.mail_host_port}"
            if self.mail_host_port
            else self.mail_host
        )
