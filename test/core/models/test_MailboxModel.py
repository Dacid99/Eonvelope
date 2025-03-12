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
import os
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher
from Emailkasten.utils import get_config


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks :attr:`core.models.MailboxModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.MailboxModel.logger", autospec=True)


@pytest.mark.django_db
def test_MailboxModel_default_creation(mailboxModel):
    """Tests the correct default creation of :class:`core.models.MailboxModel.MailboxModel`."""

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
    ],
)
def test_MailboxModel_getAvailableFetchingCriteria(
    mailboxModel, protocol, expectedFetchingCriteria
) -> None:
    """Tests :func:`core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria`.

    Args:
        protocol: The protocol parameter.
        expectedFetchingCriteria: The expected fetchingCriteria result parameter.
    """

    mailboxModel.account.protocol = protocol
    mailboxModel.account.save()
    assert mailboxModel.getAvailableFetchingCriteria() == expectedFetchingCriteria


@pytest.mark.django_db
def test_test_connection_success(mocker, mock_logger, mailboxModel):
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", autospec=True
    )
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test
    mailboxModel.is_healthy = False
    mailboxModel.save(update_fields=["is_healthy"])

    mailboxModel.test_connection()

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher_test.assert_called_once_with(mailboxModel)
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_test_connection_badProtocol(mocker, mock_logger, mailboxModel) -> None:
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher",
        autospec=True,
        side_effect=ValueError,
    )
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test

    with pytest.raises(ValueError):
        mailboxModel.test_connection()

    mock_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher_test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("test_side_effect", [MailboxError, MailAccountError])
def test_test_connection_failure(
    mocker, mock_logger, mailboxModel, test_side_effect
) -> None:
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", autospec=True
    )
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test
    mock_fetcher_test.side_effect = test_side_effect
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(test_side_effect):
        mailboxModel.test_connection()

    if test_side_effect == MailboxError:
        assert mailboxModel.is_healthy is False
    elif test_side_effect == MailAccountError:
        assert mailboxModel.account.is_healthy is False
    mock_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher_test.assert_called_once_with(mailboxModel)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_test_connection_get_fetcher_error(mocker, mock_logger, mailboxModel) -> None:
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher",
        autospec=True,
        side_effect=MailAccountError,
    )
    mock_fetcher_test = mock_get_fetcher.return_value.__enter__.return_value.test
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        mailboxModel.test_connection()

    assert mailboxModel.account.is_healthy is False
    mock_get_fetcher.assert_called_once_with(mailboxModel.account)
    mock_fetcher_test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_fetch_success(mocker, mock_logger, mailboxModel):
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", autospec=True
    )
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.return_value = [b"123", b"567", b"098", b"112233"]
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes", autospec=True
    )
    mailboxModel.is_healthy = False
    mailboxModel.save(update_fields=["is_healthy"])

    mailboxModel.fetch("criterion")

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_fetcher_fetchEmails.assert_called_once_with(mailboxModel, "criterion")
    assert mock_EMailModel_createFromBytes.call_count == 4
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_fetch_failure(mocker, faker, mock_logger, mailboxModel) -> None:
    fake_criterion = faker.word()
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher", autospec=True
    )
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.side_effect = MailboxError
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes", autospec=True
    )
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailboxError):
        mailboxModel.fetch(fake_criterion)

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is False
    mock_fetcher_fetchEmails.assert_called_once_with(mailboxModel, fake_criterion)
    mock_EMailModel_createFromBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_fetch_get_fetcher_error(mocker, mock_logger, mailboxModel) -> None:
    mock_get_fetcher = mocker.patch(
        "core.models.AccountModel.AccountModel.get_fetcher",
        autospec=True,
        side_effect=MailAccountError,
    )
    mock_fetcher_fetchEmails = (
        mock_get_fetcher.return_value.__enter__.return_value.fetchEmails
    )
    mock_fetcher_fetchEmails.return_value = [b"123", b"567", b"098", b"112233"]
    mock_EMailModel_createFromBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes", autospec=True
    )
    mailboxModel.is_healthy = True
    mailboxModel.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        mailboxModel.fetch("criterion")

    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is True
    mock_fetcher_fetchEmails.assert_not_called()
    mock_EMailModel_createFromBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_format, expectedClass",
    [
        ("mmdf", "mailbox.MMDF"),
        ("babyl", "mailbox.Babyl"),
        ("mbox", "mailbox.mbox"),
        ("mh", "mailbox.MH"),
        ("maildir", "mailbox.Maildir"),
    ],
)
def test_addFromMailboxFile_success(
    mocker,
    faker,
    override_config,
    mailboxModel,
    mock_logger,
    file_format,
    expectedClass,
) -> None:
    mock_open = mocker.mock_open()
    mocker.patch("core.models.MailboxModel.open", mock_open)
    mock_parser = mocker.Mock()
    mock_parser.iterkeys.return_value = ["key1", "second key"]
    mock_parser_class = mocker.patch(
        f"core.models.MailboxModel.{expectedClass}",
        autospec=True,
        return_value=mock_parser,
    )
    mock_EMailModel_createFromEmailBytes = mocker.patch(
        "core.models.MailboxModel.EMailModel.createFromEmailBytes", autospec=True
    )
    fake_mailbox_file = bytes(faker.sentence(7), encoding="utf-8")

    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"):
        mailboxModel.addFromMailboxFile(fake_mailbox_file, file_format)

    mock_open.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_mailbox_file))), "bw"
    )
    mock_open.return_value.write.assert_called_once_with(fake_mailbox_file)
    mock_parser_class.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_mailbox_file)))
    )
    assert mock_EMailModel_createFromEmailBytes.call_count == 2
    mock_EMailModel_createFromEmailBytes.assert_has_calls(
        [
            mocker.call(mock_parser.get_bytes("key1"), mailboxModel),
            mocker.call(mock_parser.get_bytes("second key"), mailboxModel),
        ]
    )
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_addFromMailboxFile_bad_format(
    mocker, faker, override_config, mailboxModel, mock_logger
) -> None:
    mock_open = mocker.mock_open()
    mocker.patch("core.models.MailboxModel.open", mock_open)
    mock_EMailModel_createFromEmailBytes = mocker.patch(
        "core.models.EMailModel.EMailModel.createFromEmailBytes", autospec=True
    )
    fake_mbox = bytes(faker.sentence(7), encoding="utf-8")

    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"), pytest.raises(
        ValueError
    ):
        mailboxModel.addFromMailboxFile(fake_mbox, "unimplemented")

    mock_open.assert_not_called()
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()


def test_fromData(mocker):
    mock_parseMailboxName = mocker.patch(
        "core.models.MailboxModel.parseMailboxName",
        autospec=True,
        return_value="testname",
    )

    new_mailboxModel = MailboxModel.fromData("mailboxData", None)

    mock_parseMailboxName.assert_called_once_with("mailboxData")
    assert new_mailboxModel.name == "testname"
