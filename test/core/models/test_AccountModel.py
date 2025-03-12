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
from django.db import IntegrityError
from model_bakery import baker

import core.models.AccountModel
from core.constants import EmailProtocolChoices
from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.BaseFetcher import BaseFetcher
from core.utils.fetchers.exceptions import MailAccountError
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks the :attr:`core.models.AccountModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.AccountModel.logger", autospec=True)


@pytest.fixture(name="mock_fetcher")
def fixture_mock_fetcher(mocker, faker) -> MagicMock:
    mock_fetcher = mocker.MagicMock(spec=BaseFetcher)
    mock_fetcher.__enter__.return_value = mock_fetcher
    mock_fetcher.fetchMailboxes.return_value = [word.encode() for word in faker.words()]
    return mock_fetcher


@pytest.fixture(name="mock_AccountModel_get_fetcher")
def fixture_mock_AccountModel_get_fetcher(mocker, mock_fetcher) -> MagicMock:
    return mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher",
        autospec=True,
        return_value=mock_fetcher,
    )


@pytest.mark.django_db
def test_AccountModel_default_creation(django_user_model, account):
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
    assert any(account.protocol == protocol for protocol in EmailProtocolChoices.values)
    assert account.timeout is None
    assert account.is_healthy is True
    assert account.is_favorite is False
    assert account.user is not None
    assert isinstance(account.user, django_user_model)
    assert account.updated is not None
    assert isinstance(account.updated, datetime.datetime)
    assert account.created is not None
    assert isinstance(account.created, datetime.datetime)

    assert account.mail_address in str(account)
    assert account.protocol in str(account)


@pytest.mark.django_db
def test_AccountModel_foreign_key_deletion(account):
    """Tests the on_delete foreign key constraint in :class:`core.models.AccountModel.AccountModel`."""

    assert account is not None
    account.user.delete()
    with pytest.raises(AccountModel.DoesNotExist):
        account.refresh_from_db()


@pytest.mark.django_db
def test_AccountModel_unique(django_user_model):
    """Tests the unique constraints of :class:`core.models.AccountModel.AccountModel`."""

    account_1 = baker.make(AccountModel, mail_address="abc123")
    account_2 = baker.make(AccountModel, mail_address="abc123")
    assert account_1.mail_address == account_2.mail_address
    assert account_1.user != account_2.user

    user = baker.make(django_user_model)

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
        (EmailProtocolChoices.IMAP, IMAPFetcher),
        (EmailProtocolChoices.IMAP_SSL, IMAP_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
    ],
)
def test_get_fetcher_success(
    mocker, mock_logger, account, protocol, expectedFetcherClass
):
    mocker.patch(
        f"core.models.AccountModel.{expectedFetcherClass.__name__}.__init__",
        return_value=None,
    )
    account.protocol = protocol

    fetcher = account.get_fetcher()

    assert isinstance(fetcher, expectedFetcherClass)
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_get_fetcher_bad_protocol(mock_logger, account):
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])
    account.protocol = "OTHER"

    with pytest.raises(ValueError):
        account.get_fetcher()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expectedFetcherClass",
    [
        (EmailProtocolChoices.IMAP, IMAPFetcher),
        (EmailProtocolChoices.IMAP_SSL, IMAP_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
    ],
)
def test_get_fetcher_init_failure(
    mocker, mock_logger, account, protocol, expectedFetcherClass
):
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])
    mocker.patch(
        f"core.models.AccountModel.{expectedFetcherClass.__name__}.__init__",
        side_effect=MailAccountError,
    )
    account.protocol = protocol

    with pytest.raises(MailAccountError):
        account.get_fetcher()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expectedFetcherClass",
    [
        (EmailProtocolChoices.IMAP, IMAPFetcher),
        (EmailProtocolChoices.IMAP_SSL, IMAP_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
    ],
)
def test_get_fetcher_class_success(
    mock_logger, account, protocol, expectedFetcherClass
):
    account.protocol = protocol

    fetcherClass = account.get_fetcher_class()

    assert fetcherClass == expectedFetcherClass
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_get_fetcher_class_failure(mock_logger, account):
    account.is_healthy = True
    account.protocol = "OTHER"
    account.save(update_fields=["is_healthy"])

    with pytest.raises(ValueError):
        account.get_fetcher_class()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_test_connection_success(
    mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    account.is_healthy = False
    account.save(update_fields=["is_healthy"])

    account.test_connection()

    account.refresh_from_db()
    assert account.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_test_connection_badProtocol(
    mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    mock_AccountModel_get_fetcher.side_effect = ValueError

    with pytest.raises(ValueError):
        account.test_connection()

    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_test_connection_failure(
    mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
) -> None:
    mock_fetcher.test.side_effect = MailAccountError
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        account.test_connection()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_test_connection_get_fetcher_error(
    mock_logger, account, mock_AccountModel_get_fetcher
) -> None:
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        account.test_connection()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_AccountModel_get_fetcher.return_value.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_update_mailboxes_success(
    mocker, mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    spy_MailboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )
    account.is_healthy = False
    account.save(update_fields=["is_healthy"])

    account.update_mailboxes()

    account.refresh_from_db()
    assert account.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    assert spy_MailboxModel_fromData.call_count == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    assert account.mailboxes.count() == len(mock_fetcher.fetchMailboxes.return_value)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db(transaction=True)
def test_update_mailboxes_duplicate(
    mocker, mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    baker.make(MailboxModel, account=account, name="INBOX")
    mock_fetcher.fetchMailboxes.return_value[0] = b"INBOX"
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )

    assert account.mailboxes.count() == 1

    account.update_mailboxes()

    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    assert spy_MaiboxModel_fromData.call_count == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    account.refresh_from_db()
    assert account.mailboxes.count() == len(mock_fetcher.fetchMailboxes.return_value)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_update_mailboxes_failure(
    mocker, mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    mock_fetcher.fetchMailboxes.side_effect = MailAccountError
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        account.update_mailboxes()

    account.refresh_from_db()
    assert account.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    spy_MaiboxModel_fromData.assert_not_called()
    account.refresh_from_db()
    assert account.mailboxes.count() == 0
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_update_mailboxes_get_fetcher_error(
    mocker, mock_logger, account, mock_fetcher, mock_AccountModel_get_fetcher
):
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    spy_MaiboxModel_fromData = mocker.spy(
        core.models.AccountModel.MailboxModel, "fromData"
    )
    account.is_healthy = True
    account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        account.update_mailboxes()

    account.refresh_from_db()
    assert account.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(account)
    mock_fetcher.fetchMailboxes.assert_not_called()
    spy_MaiboxModel_fromData.assert_not_called()
    account.refresh_from_db()
    assert account.mailboxes.count() == 0
    mock_logger.info.assert_called()
