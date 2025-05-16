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


"""Test module for :mod:`core.models.Mailbox`."""
from __future__ import annotations

import datetime
import mailbox
import os
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models.Account import Account
from core.models.Mailbox import Mailbox
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from core.utils.fetchers.IMAPFetcher import IMAPFetcher
from core.utils.fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from core.utils.fetchers.POP3Fetcher import POP3Fetcher
from Emailkasten.utils.workarounds import get_config

from .test_Account import mock_Account_get_fetcher, mock_fetcher


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks :attr:`core.models.Mailbox.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.Mailbox.logger", autospec=True)


@pytest.fixture
def mock_open(mocker):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open()
    mocker.patch("core.models.Mailbox.open", mock_open)
    return mock_open


@pytest.fixture
def mock_parseMailboxName(mocker, faker):
    fake_name = faker.name()
    return mocker.patch(
        "core.models.Mailbox.parseMailboxName",
        autospec=True,
        return_value=fake_name,
    )


@pytest.fixture
def mock_Email_createFromEmailBytes(mocker):
    return mocker.patch("core.models.Mailbox.Email.createFromEmailBytes", autospec=True)


@pytest.mark.django_db
def test_Mailbox_fields(fake_mailbox):
    """Tests the fields of :class:`core.models.Mailbox.Mailbox`."""

    assert fake_mailbox.name is not None
    assert fake_mailbox.account is not None
    assert isinstance(fake_mailbox.account, Account)
    assert fake_mailbox.save_attachments is get_config("DEFAULT_SAVE_ATTACHMENTS")
    assert fake_mailbox.save_toEML is get_config("DEFAULT_SAVE_TO_EML")
    assert fake_mailbox.is_favorite is False
    assert fake_mailbox.is_healthy is None
    assert isinstance(fake_mailbox.updated, datetime.datetime)
    assert fake_mailbox.updated is not None
    assert isinstance(fake_mailbox.created, datetime.datetime)
    assert fake_mailbox.created is not None


@pytest.mark.django_db
def test_Mailbox___str__(fake_mailbox):
    """Tests the string representation of :class:`core.models.Mailbox.Mailbox`."""
    assert fake_mailbox.name in str(fake_mailbox)
    assert str(fake_mailbox.account) in str(fake_mailbox)


@pytest.mark.django_db
def test_Mailbox_foreign_key_deletion(fake_mailbox):
    """Tests the on_delete foreign key constraint in :class:`core.models.Mailbox.Mailbox`."""

    assert fake_mailbox is not None
    fake_mailbox.account.delete()
    with pytest.raises(Mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_Mailbox_unique_constraints():
    """Tests the unique constraints of :class:`core.models.Mailbox.Mailbox`."""

    mailingList_1 = baker.make(Mailbox, name="abc123")
    mailingList_2 = baker.make(Mailbox, name="abc123")
    assert mailingList_1.name == mailingList_2.name
    assert mailingList_1.account != mailingList_2.account

    account = baker.make(Account)

    mailingList_1 = baker.make(Mailbox, account=account)
    mailingList_2 = baker.make(Mailbox, account=account)
    assert mailingList_1.name != mailingList_2.name
    assert mailingList_1.account == mailingList_2.account

    baker.make(Mailbox, name="abc123", account=account)
    with pytest.raises(IntegrityError):
        baker.make(Mailbox, name="abc123", account=account)


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
def test_Mailbox_getAvailableFetchingCriteria(
    fake_mailbox, protocol, expectedFetchingCriteria
):
    """Tests :func:`core.models.Mailbox.Mailbox.getAvailableFetchingCriteria`.

    Args:
        protocol: The protocol parameter.
        expectedFetchingCriteria: The expected fetchingCriteria result parameter.
    """

    fake_mailbox.account.protocol = protocol
    fake_mailbox.account.save()
    assert fake_mailbox.getAvailableFetchingCriteria() == expectedFetchingCriteria


@pytest.mark.django_db
def test_Mailbox_test_connection_success(
    fake_mailbox, mock_logger, mock_fetcher, mock_Account_get_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test_connection`
    in case of success.
    """
    fake_mailbox.is_healthy = False
    fake_mailbox.save(update_fields=["is_healthy"])

    fake_mailbox.test_connection()

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_called_once_with(fake_mailbox)
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_test_connection_badProtocol(
    fake_mailbox, mock_logger, mock_Account_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test_connection`
    in case the account of the mailbox has a bad :attr:`core.models.Account.Account.protocol` field
    and thus get_fetcher raises a :class:`ValueError`.
    """
    mock_Account_get_fetcher.side_effect = ValueError

    with pytest.raises(ValueError):
        fake_mailbox.test_connection()

    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("test_side_effect", [MailboxError, MailAccountError])
def test_Mailbox_test_connection_failure(
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    test_side_effect,
):
    """Tests :func:`core.models.Mailbox.Mailbox.test_connection`
    in case the test fails with a :class:`core.utils.fetchers.exceptions.FetcherError`.
    """
    mock_fetcher.test.side_effect = test_side_effect
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(test_side_effect):
        fake_mailbox.test_connection()

    if test_side_effect == MailboxError:
        assert fake_mailbox.is_healthy is False
    elif test_side_effect == MailAccountError:
        assert fake_mailbox.account.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_called_once_with(fake_mailbox)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_test_connection_get_fetcher_error(
    fake_mailbox, mock_logger, mock_Account_get_fetcher, mock_fetcher
):
    """Tests :func:`core.models.Mailbox.Mailbox.test_connection`
    in case :func:`core.models.Account.Account.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_mailbox.test_connection()

    assert fake_mailbox.account.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_fetch_success(
    faker,
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    mock_Email_createFromEmailBytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case of success.
    """
    fake_criterion = faker.word()
    fake_mailbox.is_healthy = False
    fake_mailbox.save(update_fields=["is_healthy"])

    fake_mailbox.fetch(fake_criterion)

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetchEmails.assert_called_once_with(fake_mailbox, fake_criterion)
    assert mock_Email_createFromEmailBytes.call_count == len(
        mock_fetcher.fetchEmails.return_value
    )
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_fetch_failure(
    faker,
    fake_mailbox,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    mock_Email_createFromEmailBytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case fetching fails with a :class:`core.utils.fetchers.exceptions.MailboxError`.
    """
    fake_criterion = faker.word()
    mock_fetcher.fetchEmails.side_effect = MailboxError
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailboxError):
        fake_mailbox.fetch(fake_criterion)

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetchEmails.assert_called_once_with(fake_mailbox, fake_criterion)
    mock_Email_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_fetch_get_fetcher_error(
    fake_mailbox,
    mock_logger,
    mock_Account_get_fetcher,
    mock_fetcher,
    mock_Email_createFromEmailBytes,
):
    """Tests :func:`core.models.Mailbox.Mailbox.fetch`
    in case :func:`core.models.Account.Account.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError
    fake_mailbox.is_healthy = True
    fake_mailbox.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_mailbox.fetch("criterion")

    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_mailbox.account)
    mock_fetcher.fetchEmails.assert_not_called()
    mock_Email_createFromEmailBytes.assert_not_called()
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
def test_Mailbox_addFromMailboxFile_success(
    mocker,
    faker,
    override_config,
    fake_file_bytes,
    fake_mailbox,
    mock_logger,
    mock_open,
    mock_Email_createFromEmailBytes,
    file_format,
    expectedClass,
):
    """Tests :func:`core.models.Account.Account.addFromMailboxFile`
    in case of success.
    """
    mock_parser = mocker.Mock(spec=expectedClass)
    fake_keys = faker.words()
    mock_parser.iterkeys.return_value = fake_keys
    mock_parser_class = mocker.patch(
        f"core.models.Mailbox.mailbox.{expectedClass.__name__}",
        autospec=True,
        return_value=mock_parser,
    )

    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"):
        fake_mailbox.addFromMailboxFile(fake_file_bytes, file_format)

    mock_open.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_file_bytes))), "bw"
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    mock_parser_class.assert_called_once_with(
        os.path.join("/tmp/", str(hash(fake_file_bytes)))
    )
    assert mock_Email_createFromEmailBytes.call_count == len(fake_keys)
    mock_Email_createFromEmailBytes.assert_has_calls(
        [mocker.call(mock_parser.get_bytes(key), fake_mailbox) for key in fake_keys]
    )
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_addFromMailboxFile_bad_format(
    override_config,
    fake_file_bytes,
    fake_mailbox,
    mock_open,
    mock_logger,
    mock_Email_createFromEmailBytes,
):
    """Tests :func:`core.models.Account.Account.addFromMailboxFile`
    in case of the mailbox file format is an unsupported format.
    """
    with override_config(TEMPORARY_STORAGE_DIRECTORY="/tmp/"), pytest.raises(
        ValueError
    ):
        fake_mailbox.addFromMailboxFile(fake_file_bytes, "unimplemented")

    mock_open.assert_not_called()
    mock_Email_createFromEmailBytes.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Mailbox_createFromData_success(
    faker, fake_account, mock_logger, mock_parseMailboxName
):
    """Tests :func:`core.models.Account.Account.createFromData`
    in case of success.
    """
    fake_name_bytes = faker.name().encode()

    assert Mailbox.objects.count() == 0

    new_mailbox = Mailbox.createFromData(fake_name_bytes, fake_account)

    assert Mailbox.objects.count() == 1
    assert new_mailbox.pk is not None
    mock_parseMailboxName.assert_called_once_with(fake_name_bytes)
    assert new_mailbox.name == mock_parseMailboxName.return_value
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Mailbox_createFromData_duplicate(
    faker, fake_mailbox, mock_logger, mock_parseMailboxName
):
    """Tests :func:`core.models.Account.Account.createFromData`
    in case of data that is already in the db.
    """
    fake_name_bytes = faker.name().encode()

    assert Mailbox.objects.count() == 1

    mock_parseMailboxName.return_value = fake_mailbox.name

    new_mailbox = Mailbox.createFromData(fake_name_bytes, fake_mailbox.account)

    assert Mailbox.objects.count() == 1
    assert new_mailbox.pk is not None
    mock_parseMailboxName.assert_called_once_with(fake_name_bytes)
    assert new_mailbox == fake_mailbox
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Mailbox_createFromData_no_account(faker, mock_parseMailboxName):
    """Tests :func:`core.models.Account.Account.createFromData`
    in case of data that is already in the db.
    """
    fake_name_bytes = faker.name().encode()

    assert Mailbox.objects.count() == 0

    with pytest.raises(ValueError):
        Mailbox.createFromData(fake_name_bytes, Account())

    assert Mailbox.objects.count() == 0
    mock_parseMailboxName.assert_not_called()


@pytest.mark.django_db
def test_Mailbox_get_absolute_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_url`."""
    result = fake_mailbox.get_absolute_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-detail",
        kwargs={"pk": fake_mailbox.pk},
    )


@pytest.mark.django_db
def test_Mailbox_get_absolute_edit_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_edit_url`."""
    result = fake_mailbox.get_absolute_edit_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-edit",
        kwargs={"pk": fake_mailbox.pk},
    )


@pytest.mark.django_db
def test_Mailbox_get_absolute_list_url(fake_mailbox):
    """Tests :func:`core.models.Mailbox.Mailbox.get_absolute_list_url`."""
    result = fake_mailbox.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_mailbox.BASENAME}-filter-list",
    )
