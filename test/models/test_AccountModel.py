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

"""Test module for :mod:`core.models.AccountModel`.

Fixtures:
    :func:`fixture_accountModel`: Creates an :class:`core.models.AccountModel.AccountModel` instance for testing.
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError, connection, transaction
from model_bakery import baker

import core.models.AccountModel
from core.constants import MailFetchingProtocols
from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(name="mock_logger")
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks :attr:`core.models.AccountModel.logger`.

    Returns:
        The mocker logger instance.
    """
    return mocker.patch("core.models.AccountModel.logger")


@pytest.fixture(name="account")
def fixture_accountModel() -> AccountModel:
    """Creates an :class:`core.models.AccountModel.AccountModel` .

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel)


@pytest.mark.django_db
def test_AccountModel_creation(account):
    """Tests the correct default creation of :class:`core.models.AccountModel.AccountModel`."""

    assert account.mail_address is not None
    assert isinstance(account.mail_address, str)
    assert account.password is not None
    assert isinstance(account.password, str)
    assert account.mail_host is not None
    assert isinstance(account.mail_host, str)
    assert account.mail_host_port is None
    assert account.protocol is not None
    assert isinstance(account.protocol, str)
    assert any(
        account.protocol == protocol for protocol, _ in AccountModel.PROTOCOL_CHOICES
    )
    assert account.timeout is None
    assert account.is_healthy is True
    assert account.is_favorite is False
    assert account.user is not None
    assert isinstance(account.user, User)
    assert account.updated is not None
    assert isinstance(account.updated, datetime.datetime)
    assert account.created is not None
    assert isinstance(account.created, datetime.datetime)

    assert account.mail_address in str(account)
    assert account.mail_host in str(account)
    assert account.protocol in str(account)


@pytest.mark.django_db
def test_AccountModel_foreign_key_deletion(account):
    """Tests the on_delete foreign key constraint in :class:`core.models.AccountModel.AccountModel`."""

    assert account is not None
    account.user.delete()
    with pytest.raises(AccountModel.DoesNotExist):
        account.refresh_from_db()


@pytest.mark.django_db
def test_AccountModel_unique():
    """Tests the unique constraints of :class:`core.models.AccountModel.AccountModel`."""

    account_1 = baker.make(AccountModel, mail_address="abc123")
    account_2 = baker.make(AccountModel, mail_address="abc123")
    assert account_1.mail_address == account_2.mail_address
    assert account_1.user != account_2.user

    user = baker.make(User)

    account_1 = baker.make(AccountModel, user=user)
    account_2 = baker.make(AccountModel, user=user)
    assert account_1.mail_address != account_2.mail_address
    assert account_1.user == account_2.user

    baker.make(AccountModel, mail_address="abc123", user=user)
    with pytest.raises(IntegrityError):
        baker.make(AccountModel, mail_address="abc123", user=user)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expectedFetcherClass",
    [
        (MailFetchingProtocols.IMAP, IMAPFetcher),
        (MailFetchingProtocols.IMAP_SSL, IMAP_SSL_Fetcher),
        (MailFetchingProtocols.POP3, POP3Fetcher),
        (MailFetchingProtocols.POP3_SSL, POP3_SSL_Fetcher),
    ],
)
def test_get_fetcher_success(mock_logger, account, protocol, expectedFetcherClass):
    account.protocol = protocol

    fetcher = account.get_fetcher()

    assert isinstance(fetcher, expectedFetcherClass)
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_get_fetcher_failure(mock_logger, account):
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])
    account.protocol = "OTHER"

    with pytest.raises(ValueError):
        account.get_fetcher()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_test_connection_success(mocker, mock_logger, account):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")

    account.test_connection()

    mock_get_fetcher.assert_called_once_with()
    mock_get_fetcher.return_value.__enter__.return_value.test.assert_called_once_with()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_test_connection_failure(mocker, mock_logger, account):
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", side_effect=ValueError
    )

    account.test_connection()

    account.refresh_from_db()
    mock_get_fetcher.assert_called_once_with()
    mock_get_fetcher.return_value.__enter__.return_value.test.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_update_mailboxes_success(mocker, mock_logger, account):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetchMailboxes = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchMailboxes
    )
    mock_fetchMailboxes.return_value = [b"INBOX", b"Trash", b"Archive"]
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )

    account.update_mailboxes()

    mock_fetchMailboxes.assert_called_once_with()
    assert spy_MaiboxModel_fromData.call_count == 3
    account.refresh_from_db()
    assert account.mailboxes.count() == 3
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db(transaction=True)
def test_update_mailboxes_duplicate(mocker, mock_logger, account):
    baker.make(MailboxModel, account=account, name="INBOX")
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetchMailboxes = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchMailboxes
    )
    mock_fetchMailboxes.return_value = [b"INBOX", b"Trash", b"Archive"]
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )

    account.update_mailboxes()

    mock_fetchMailboxes.assert_called_once_with()
    assert spy_MaiboxModel_fromData.call_count == 3
    account.refresh_from_db()
    assert account.mailboxes.count() == 3
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_update_mailboxes_exception(mocker, mock_logger, account):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetchMailboxes = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchMailboxes
    )
    mock_fetchMailboxes.side_effect = Exception
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )

    with pytest.raises(Exception):
        account.update_mailboxes()

    mock_fetchMailboxes.assert_called_once_with()
    spy_MaiboxModel_fromData.assert_not_called()
    account.refresh_from_db()
    assert account.mailboxes.count() == 0
    mock_logger.info.assert_called()
