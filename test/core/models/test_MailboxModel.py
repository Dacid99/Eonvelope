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
    :func:`fixture_mailboxModelModel`: Creates an :class:`core.models.MailboxModel.MailboxModel` instance for testing.
"""
from __future__ import annotations

import datetime
import mailbox
import os
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher
from Emailkasten.utils import get_config

from .test_AccountModel import mock_AccountModel_get_fetcher, mock_fetcher


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks :attr:`core.models.MailboxModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.MailboxModel.logger", autospec=True)


@pytest.fixture
def mock_open(mocker):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open()
    mocker.patch("core.models.MailboxModel.open", mock_open)
    return mock_open


@pytest.fixture
def mock_EMailModel_createFromEmailBytes(mocker):
    return mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes", autospec=True
    )


@pytest.mark.django_db
def test_MailboxModel_fields(mailboxModel):
    """Tests the fields of :class:`core.models.MailboxModel.MailboxModel`."""

    assert mailboxModel.name is not None
    assert mailboxModel.account is not None
    assert isinstance(mailboxModel.account, AccountModel)
    assert mailboxModel.save_attachments is get_config("DEFAULT_SAVE_ATTACHMENTS")
    assert mailboxModel.save_toEML is get_config("DEFAULT_SAVE_TO_EML")
    assert mailboxModel.is_favorite is False
    assert mailboxModel.is_healthy is True
    assert isinstance(mailboxModel.updated, datetime.datetime)
    assert mailboxModel.updated is not None
    assert isinstance(mailboxModel.created, datetime.datetime)
    assert mailboxModel.created is not None


@pytest.mark.django_db
def test_MailboxModel___str__(mailboxModel):
    """Tests the string representation of :class:`core.models.MailboxModel.MailboxModel`."""
    assert mailboxModel.name in str(mailboxModel)
    assert str(mailboxModel.account) in str(mailboxModel)


@pytest.mark.django_db
def test_MailboxModel_foreign_key_deletion(mailboxModel):
    """Tests the on_delete foreign key constraint in :class:`core.models.MailboxModel.MailboxModel`."""

    assert mailboxModel is not None
    mailboxModel.account.delete()
    with pytest.raises(MailboxModel.DoesNotExist):
        mailboxModel.refresh_from_db()


@pytest.mark.django_db
def test_MailboxModel_unique_constraints():
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
    ],
)
def test_MailboxModel_getAvailableFetchingCriteria(
    mailboxModel, protocol, expectedFetchingCriteria
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria`.

    Args:
        protocol: The protocol parameter.
        expectedFetchingCriteria: The expected fetchingCriteria result parameter.
    """

    mailboxModel.account.protocol = protocol
    mailboxModel.account.save()
    assert mailboxModel.getAvailableFetchingCriteria() == expectedFetchingCriteria


@pytest.mark.django_db
def test_MailboxModel_test_connection_success(
    mailboxModel, mock_logger, mock_fetcher, mock_AccountModel_get_fetcher
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.test_connection`
    in case of success.
    """
    mailboxModel.is_healthy = False
    mailboxModel.save(update_fields=["is_healthy"])

    mailboxModel.test_connection()

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.test.assert_called_once_with(mailboxModel)
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_MailboxModel_test_connection_badProtocol(
    mailboxModel, mock_logger, mock_AccountModel_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.test_connection`
    in case the account of the mailbox has a bad :attr:`core.models.AccountModel.AccountModel.protocol` field
    and thus get_fetcher raises a :class:`ValueError`.
    """
    mock_AccountModel_get_fetcher.side_effect = ValueError

    with pytest.raises(ValueError):
        mailboxModel.test_connection()

    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("test_side_effect", [MailboxError, MailAccountError])
def test_MailboxModel_test_connection_failure(
    mailboxModel,
    mock_logger,
    mock_AccountModel_get_fetcher,
    mock_fetcher,
    test_side_effect,
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.test_connection`
    in case the test fails with a :class:`core.utils.fetchers.exceptions.FetcherError`.
    """
    mock_fetcher.test.side_effect = test_side_effect
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(test_side_effect):
        mailboxModel.test_connection()

    if test_side_effect == MailboxError:
        assert mailboxModel.is_healthy is False
    elif test_side_effect == MailAccountError:
        assert mailboxModel.account.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.test.assert_called_once_with(mailboxModel)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_MailboxModel_test_connection_get_fetcher_error(
    mailboxModel, mock_logger, mock_AccountModel_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.test_connection`
    in case :func:`core.models.AccountModel.AccountModel.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        mailboxModel.test_connection()

    assert mailboxModel.account.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_MailboxModel_fetch_success(
    faker,
    mailboxModel,
    mock_logger,
    mock_AccountModel_get_fetcher,
    mock_fetcher,
    mock_EMailModel_createFromEmailBytes,
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.fetch`
    in case of success.
    """
    fake_criterion = faker.word()
    mailboxModel.is_healthy = False
    mailboxModel.save(update_fields=["is_healthy"])

    mailboxModel.fetch(fake_criterion)

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.fetchEmails.assert_called_once_with(mailboxModel, fake_criterion)
    assert mock_EMailModel_createFromEmailBytes.call_count == len(
        mock_fetcher.fetchEmails.return_value
    )
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_MailboxModel_fetch_failure(
    faker,
    mailboxModel,
    mock_logger,
    mock_fetcher,
    mock_AccountModel_get_fetcher,
    mock_EMailModel_createFromEmailBytes,
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.fetch`
    in case fetching fails with a :class:`core.utils.fetchers.exceptions.MailboxError`.
    """
    fake_criterion = faker.word()
    mock_fetcher.fetchEmails.side_effect = MailboxError
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailboxError):
        mailboxModel.fetch(fake_criterion)

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is False
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.fetchEmails.assert_called_once_with(mailboxModel, fake_criterion)
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_MailboxModel_fetch_get_fetcher_error(
    mailboxModel,
    mock_logger,
    mock_AccountModel_get_fetcher,
    mock_fetcher,
    mock_EMailModel_createFromEmailBytes,
):
    """Tests :func:`core.models.MailboxModel.MailboxModel.fetch`
    in case :func:`core.models.AccountModel.AccountModel.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_AccountModel_get_fetcher.side_effect = MailAccountError
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        mailboxModel.fetch("criterion")

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_AccountModel_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher.fetchEmails.assert_not_called()
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format, expectedClass",
    [
        ("mmdf", mailbox.MMDF),
        ("babyl", mailbox.Babyl),
        ("mbox", mailbox.mbox),
        ("mh", mailbox.MH),
        ("maildir", mailbox.Maildir),
    ],
)
def test_MailboxModel_addFromMailboxFile_success(
    mocker,
    faker,
    override_config,
    fake_file_bytes,
    mailboxModel,
    mock_logger,
    mock_open,
    mock_EMailModel_createFromEmailBytes,
    file_format,
    expectedClass,
):
    """Tests :func:`core.models.AccountModel.AccountModel.addFromMailboxFile`
    in case of success.
    """
    mock_parser = mocker.Mock(spec=expectedClass)
    fake_keys = faker.words()
    mock_parser.iterkeys.return_value = fake_keys
    mock_parser_class = mocker.patch(
        f"core.models.MailboxModel.mailbox.{expectedClass.__name__}",
        autospec=True,
        return_value=mock_parser,
    )

    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"):
        mailboxModel.addFromMailboxFile(fake_file_bytes, file_format)

    mock_open.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_file_bytes))), "bw"
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    mock_parser_class.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_file_bytes)))
    )
    assert mock_EMailModel_createFromEmailBytes.call_count == len(fake_keys)
    mock_EMailModel_createFromEmailBytes.assert_has_calls(
        [mocker.call(mock_parser.get_bytes(key), mailboxModel) for key in fake_keys]
    )
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_MailboxModel_addFromMailboxFile_bad_format(
    override_config,
    fake_file_bytes,
    mailboxModel,
    mock_open,
    mock_logger,
    mock_EMailModel_createFromEmailBytes,
):
    """Tests :func:`core.models.AccountModel.AccountModel.addFromMailboxFile`
    in case of the mailbox file format is an unsupported format.
    """
    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"), pytest.raises(
        ValueError
    ):
        mailboxModel.addFromMailboxFile(fake_file_bytes, "unimplemented")

    mock_open.assert_not_called()
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()


def test_MailboxModel_fromData(mocker):
    """Tests :func:`core.models.AccountModel.AccountModel.fromData`
    in case of success.
    """
    mock_parseMailboxName = mocker.patch(
        "core.models.MailboxModel.parseMailboxName",
        autospec=True,
        return_value="testname",
    )

    new_mailboxModel = MailboxModel.fromData("mailboxData", None)

    mock_parseMailboxName.assert_called_once_with("mailboxData")
    assert new_mailboxModel.name == "testname"


@pytest.mark.django_db
def test_MailboxModel_get_absolute_url(mailboxModel):
    """Tests :func:`core.models.MailboxModel.MailboxModel.get_absolute_url`."""
    result = mailboxModel.get_absolute_url()

    assert result == reverse(
        f"web:{mailboxModel.BASENAME}-detail",
        kwargs={"pk": mailboxModel.pk},
    )


@pytest.mark.django_db
def test_MailboxModel_get_absolute_edit_url(mailboxModel):
    """Tests :func:`core.models.MailboxModel.MailboxModel.get_absolute_edit_url`."""
    result = mailboxModel.get_absolute_edit_url()

    assert result == reverse(
        f"web:{mailboxModel.BASENAME}-edit",
        kwargs={"pk": mailboxModel.pk},
    )


@pytest.mark.django_db
def test_MailboxModel_get_absolute_list_url(mailboxModel):
    """Tests :func:`core.models.MailboxModel.MailboxModel.get_absolute_list_url`."""
    result = mailboxModel.get_absolute_list_url()

    assert result == reverse(
        f"web:{mailboxModel.BASENAME}-filter-list",
    )
