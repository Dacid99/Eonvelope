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


"""Test module for :mod:`core.models.MailboxModel`.

Fixtures:
    :func:`fixture_mailboxModel`: Creates an :class:`core.models.MailboxModel.MailboxModel` instance for testing.
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.constants import TestStatusCodes
from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher
from core.utils.mailParsing import parseMailboxName
from Emailkasten.utils import get_config

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(name="mock_logger")
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks :attr:`core.models.MailboxModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.MailboxModel.logger")


@pytest.fixture(name="mailbox")
def fixture_mailboxModel() -> MailboxModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailbox instance for testing.
    """
    return baker.make(MailboxModel)


@pytest.mark.django_db
def test_MailboxModel_creation(mailbox):
    """Tests the correct default creation of :class:`core.models.MailboxModel.MailboxModel`."""

    assert mailbox.name is not None
    assert mailbox.account is not None
    assert isinstance(mailbox.account, AccountModel)
    assert mailbox.save_attachments is get_config("DEFAULT_SAVE_ATTACHMENTS")
    assert mailbox.save_toEML is get_config("DEFAULT_SAVE_TO_EML")
    assert mailbox.is_favorite is False
    assert mailbox.is_healthy is True
    assert isinstance(mailbox.updated, datetime.datetime)
    assert mailbox.updated is not None
    assert isinstance(mailbox.created, datetime.datetime)
    assert mailbox.created is not None

    assert mailbox.name in str(mailbox)
    assert str(mailbox.account) in str(mailbox)


@pytest.mark.django_db
def test_MailboxModel_foreign_key_deletion(mailbox):
    """Tests the on_delete foreign key constraint in :class:`core.models.MailboxModel.MailboxModel`."""

    assert mailbox is not None
    mailbox.account.delete()
    with pytest.raises(MailboxModel.DoesNotExist):
        mailbox.refresh_from_db()


@pytest.mark.django_db
def test_MailboxModel_unique():
    """Tests the unique constraints of :class:`core.models.MailboxModel.MailboxModel`."""

    mailingList_1 = baker.make(MailboxModel, name="abc123")
    mailingList_2 = baker.make(MailboxModel, name="abc123")
    assert mailingList_1.name == mailingList_2.name
    assert mailingList_1.account != mailingList_2.account

    account = baker.make(AccountModel)

    mailingList_1 = baker.make(MailboxModel, account=account)
    mailingList_2 = baker.make(MailboxModel, account=account)
    assert mailingList_1.name != mailingList_2.name
    assert mailingList_1.account == mailingList_2.account

    baker.make(MailboxModel, name="abc123", account=account)
    with pytest.raises(IntegrityError):
        baker.make(MailboxModel, name="abc123", account=account)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expectedFetchingCriteria",
    [
        (IMAPFetcher.PROTOCOL, IMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (IMAP_SSL_Fetcher.PROTOCOL, IMAP_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
        ("EXCHANGE", []),
    ],
)
def test_MailboxModel_getAvailableFetchingCriteria(
    mailbox, protocol: str, expectedFetchingCriteria: list[str]
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria`.

    Args:
        protocol: The protocol parameter.
        expectedFetchingCriteria: The expected fetchingCriteria result parameter.
    """

    mailbox.account.protocol = protocol
    mailbox.account.save()
    assert mailbox.getAvailableFetchingCriteria() == expectedFetchingCriteria


@pytest.mark.django_db
def test_fetch(mocker, mailbox):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")

    mailbox.fetch("ALL")

    mock_get_fetcher.assert_called_once()
    mock_get_fetcher.return_value.__enter__.return_value.fetchEmails.assert_called_once()


@pytest.mark.django_db
def test_test_connection_success(mocker, mock_logger, mailbox):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test
    mock_fetcher_test.return_value = TestStatusCodes.OK

    result = mailbox.test_connection()

    assert result == TestStatusCodes.OK
    mock_get_fetcher.assert_called_once_with()
    mock_fetcher_test.assert_called_once_with(mailbox)
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_test_connection_failure(mocker, mock_logger, mailbox):
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", side_effect=ValueError
    )
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test

    result = mailbox.test_connection()

    assert result == TestStatusCodes.ERROR
    mock_get_fetcher.assert_called_once_with()
    mock_fetcher_test.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_fetch_success(mocker, mock_logger, mailbox):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.return_value = [b"123", b"567", b"098", b"112233"]
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes"
    )

    mailbox.fetch("criterion")

    mock_fetcher_fetchEmails.assert_called_once_with(mailbox, "criterion")
    mock_EMailModel_createFromBytes.call_count == 4
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_fetch_duplicate(mocker, mock_logger, mailbox):
    mock_get_fetcher = mocker.patch("core.models.AccountModel.AccountModel.get_fetcher")
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.return_value = [b"123", b"567", b"098", b"112233"]
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes"
    )
    mock_EMailModel_createFromBytes.side_effect = IntegrityError

    mailbox.fetch("criterion")

    mock_fetcher_fetchEmails.assert_called_once_with(mailbox, "criterion")
    mock_EMailModel_createFromBytes.call_count == 4
    mock_logger.info.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_fetch_exception(mocker, mock_logger, mailbox):
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", side_effect=Exception
    )
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.return_value = [b"123", b"567", b"098", b"112233"]
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes"
    )

    with pytest.raises(Exception):
        mailbox.fetch("criterion")

    mock_fetcher_fetchEmails.assert_not_called()
    mock_EMailModel_createFromBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


def test_fromData(mocker):
    mock_parseMailboxName = mocker.patch(
        "core.models.MailboxModel.parseMailboxName", return_value="testname"
    )

    new_mailbox = MailboxModel.fromData("mailboxData", None)

    mock_parseMailboxName.assert_called_once_with("mailboxData")
    assert new_mailbox.name == "testname"
