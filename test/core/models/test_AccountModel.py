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


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks the :attr:`core.models.AccountModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.AccountModel.logger", autospec=True)


@pytest.fixture
def mock_fetcher(mocker, faker) -> MagicMock:
    """Fixture mocking a :class:`core.utils.fetchers.BaseFetcher.BaseFetcher` instance.

    Returns:
        The mocked fetcher instance.
    """
    mock_fetcher = mocker.MagicMock(spec=BaseFetcher)
    mock_fetcher.__enter__.return_value = mock_fetcher
    mock_fetcher.fetchEmails.return_value = [text.encode() for text in faker.texts()]
    mock_fetcher.fetchMailboxes.return_value = [word.encode() for word in faker.words()]
    return mock_fetcher


@pytest.fixture
def mock_AccountModel_get_fetcher(mocker, mock_fetcher) -> MagicMock:
    """Fixture mocking a :func:`core.models.AccountModel.AccountModel.get_fetcher`.

    Returns:
        The mocked function.
    """
    return mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher",
        autospec=True,
        return_value=mock_fetcher,
    )


@pytest.fixture
def spy_MailboxModel_fromData(mocker):
    """Fixture spying on :func:`core.models.AccountModel.MailboxModel.fromData` instance.

    Returns:
        The spied on function.
    """
    return mocker.spy(core.models.AccountModel.MailboxModel, "fromData")


@pytest.mark.django_db
def test_AccountModel_fields(django_user_model, accountModel):
    """Tests the fields of :class:`core.models.AccountModel.AccountModel`."""
    assert accountModel.mail_address is not None
    assert isinstance(accountModel.mail_address, str)
    assert accountModel.password is not None
    assert isinstance(accountModel.password, str)
    assert accountModel.mail_host is not None
    assert isinstance(accountModel.mail_host, str)
    assert accountModel.mail_host_port is None
    assert accountModel.protocol is not None
    assert isinstance(accountModel.protocol, str)
    assert any(
        accountModel.protocol == protocol for protocol in EmailProtocolChoices.values
    )
    assert accountModel.timeout is None
    assert accountModel.is_healthy is True
    assert accountModel.is_favorite is False
    assert accountModel.user is not None
    assert isinstance(accountModel.user, django_user_model)
    assert accountModel.updated is not None
    assert isinstance(accountModel.updated, datetime.datetime)
    assert accountModel.created is not None
    assert isinstance(accountModel.created, datetime.datetime)


@pytest.mark.django_db
def test_AccountModel___str__(accountModel):
    """Tests the string representation of :class:`core.models.AccountModel.AccountModel`."""
    assert accountModel.mail_address in str(accountModel)
    assert accountModel.protocol in str(accountModel)


@pytest.mark.django_db
def test_AccountModel_foreign_key_deletion(accountModel):
    """Tests the on_delete foreign key constraint in :class:`core.models.AccountModel.AccountModel`."""

    assert accountModel is not None
    accountModel.user.delete()
    with pytest.raises(AccountModel.DoesNotExist):
        accountModel.refresh_from_db()


@pytest.mark.django_db
def test_AccountModel_unique_constraints(django_user_model):
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
def test_AccountModel_get_fetcher_success(
    mocker, mock_logger, accountModel, protocol, expectedFetcherClass
):
    """Tests :func:`core.models.AccountModel.AccountModel.get_fetcher`
    in case of success.
    """
    mocker.patch(
        f"core.models.AccountModel.{expectedFetcherClass.__name__}.__init__",
        return_value=None,
    )
    accountModel.protocol = protocol

    fetcher = accountModel.get_fetcher()

    assert isinstance(fetcher, expectedFetcherClass)
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_AccountModel_get_fetcher_bad_protocol(mock_logger, accountModel):
    """Tests :func:`core.models.AccountModel.AccountModel.get_fetcher`
    in case the account has a bad :attr:`core.models.AccountModel.AccountModel.protocol` field.
    """
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])
    accountModel.protocol = "OTHER"

    with pytest.raises(ValueError):
        accountModel.get_fetcher()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
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
def test_AccountModel_get_fetcher_init_failure(
    mocker, mock_logger, accountModel, protocol, expectedFetcherClass
):
    """Tests :func:`core.models.AccountModel.AccountModel.get_fetcher`
    in case the fetcher fails to construct with a :class:`core.utils.fetcher.exceptions.MailAccountError`.
    """
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])
    mocker.patch(
        f"core.models.AccountModel.{expectedFetcherClass.__name__}.__init__",
        side_effect=MailAccountError,
    )
    accountModel.protocol = protocol

    with pytest.raises(MailAccountError):
        accountModel.get_fetcher()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
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
def test_AccountModel_get_fetcher_class_success(
    accountModel, mock_logger, protocol, expectedFetcherClass
):
    """Tests :func:`core.models.AccountModel.AccountModel.get_fetcher_class`
    in case of success.
    """
    accountModel.protocol = protocol

    fetcherClass = accountModel.get_fetcher_class()

    assert fetcherClass == expectedFetcherClass
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_AccountModel_get_fetcher_class_bad_protocol(accountModel, mock_logger):
    """Tests :func:`core.models.AccountModel.AccountModel.get_fetcher_class`
    in case the account has a bad :attr:`core.models.AccountModel.AccountModel.protocol` field.
    """
    accountModel.is_healthy = True
    accountModel.protocol = "OTHER"
    accountModel.save(update_fields=["is_healthy"])

    with pytest.raises(ValueError):
        accountModel.get_fetcher_class()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_AccountModel_test_connection_success(
    accountModel, mock_logger, mock_fetcher, mock_AccountModel_get_fetcher
):
    """Tests :func:`core.models.AccountModel.AccountModel.test_connection`
    in case of success.
    """
    accountModel.is_healthy = False
    accountModel.save(update_fields=["is_healthy"])

    accountModel.test_connection()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_AccountModel_test_connection_badProtocol(
    accountModel, mock_logger, mock_fetcher, mock_AccountModel_get_fetcher
):
    """Tests :func:`core.models.AccountModel.AccountModel.test_connection`
    in case of the account has a bad :attr:`core.models.AccountModel.AccountModel.protocol` field and raises a :class:`ValueError`.
    """
    mock_AccountModel_get_fetcher.side_effect = ValueError

    with pytest.raises(ValueError):
        accountModel.test_connection()

    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_AccountModel_test_connection_failure(
    accountModel, mock_logger, mock_fetcher, mock_AccountModel_get_fetcher
):
    """Tests :func:`core.models.AccountModel.AccountModel.test_connection`
    in case of the test fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_fetcher.test.side_effect = MailAccountError
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        accountModel.test_connection()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_AccountModel_test_connection_get_fetcher_error(
    accountModel, mock_logger, mock_AccountModel_get_fetcher
):
    """Tests :func:`core.models.AccountModel.AccountModel.test_connection`
    in case the :func:`core.models.AccountModel.AccountModel.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        accountModel.test_connection()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_AccountModel_get_fetcher.return_value.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_AccountModel_update_mailboxes_success(
    accountModel,
    mock_logger,
    mock_fetcher,
    mock_AccountModel_get_fetcher,
    spy_MailboxModel_fromData,
):
    """Tests :func:`core.models.AccountModel.AccountModel.update_mailboxes`
    in case of success.
    """
    accountModel.is_healthy = False
    accountModel.save(update_fields=["is_healthy"])

    accountModel.update_mailboxes()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is True
    assert accountModel.mailboxes.count() == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    assert spy_MailboxModel_fromData.call_count == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db(transaction=True)
def test_AccountModel_update_mailboxes_duplicate(
    accountModel,
    mock_logger,
    mock_fetcher,
    mock_AccountModel_get_fetcher,
    spy_MailboxModel_fromData,
):
    """Tests :func:`core.models.AccountModel.AccountModel.update_mailboxes`
    in case of a fetched mailbox already being in the db.
    """
    baker.make(MailboxModel, account=accountModel, name="INBOX")
    mock_fetcher.fetchMailboxes.return_value[0] = b"INBOX"

    assert accountModel.mailboxes.count() == 1

    accountModel.update_mailboxes()

    accountModel.refresh_from_db()
    assert accountModel.mailboxes.count() == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    assert spy_MailboxModel_fromData.call_count == len(
        mock_fetcher.fetchMailboxes.return_value
    )
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_AccountModel_update_mailboxes_failure(
    accountModel,
    mock_logger,
    mock_fetcher,
    mock_AccountModel_get_fetcher,
    spy_MailboxModel_fromData,
):
    """Tests :func:`core.models.AccountModel.AccountModel.update_mailboxes`
    in case fetching mailboxes fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_fetcher.fetchMailboxes.side_effect = MailAccountError
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        accountModel.update_mailboxes()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is False
    assert accountModel.mailboxes.count() == 0
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.fetchMailboxes.assert_called_once_with()
    spy_MailboxModel_fromData.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_AccountModel_update_mailboxes_get_fetcher_error(
    accountModel,
    mock_logger,
    mock_fetcher,
    mock_AccountModel_get_fetcher,
    spy_MailboxModel_fromData,
):
    """Tests :func:`core.models.AccountModel.AccountModel.update_mailboxes`
    in case :func:`core.models.AccountModel.AccountModel.get_fetcher`
    fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    accountModel.is_healthy = True
    accountModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        accountModel.update_mailboxes()

    accountModel.refresh_from_db()
    assert accountModel.is_healthy is True
    assert accountModel.mailboxes.count() == 0
    mock_AccountModel_get_fetcher.assert_called_once_with(accountModel)
    mock_fetcher.fetchMailboxes.assert_not_called()
    spy_MailboxModel_fromData.assert_not_called()
    mock_logger.info.assert_called()
