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

"""Test module for :mod:`core.models.Account`."""

from __future__ import annotations

import datetime

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.constants import EmailProtocolChoices
from core.models import Account, Mailbox
from core.utils.fetchers import (
    BaseFetcher,
    ExchangeFetcher,
    IMAP4_SSL_Fetcher,
    IMAP4Fetcher,
    POP3_SSL_Fetcher,
    POP3Fetcher,
)
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """The mocked :attr:`core.models.Account.logger`."""
    return mocker.patch("core.models.Account.logger", autospec=True)


@pytest.fixture
def mock_fetcher(mocker, faker):
    """A mock :class:`core.utils.fetchers.BaseFetcher.BaseFetcher` instance."""
    mock_fetcher = mocker.MagicMock(spec=BaseFetcher)
    mock_fetcher.__enter__.return_value = mock_fetcher
    mock_fetcher.fetch_emails.return_value = [text.encode() for text in faker.texts()]
    mock_fetcher.fetch_mailboxes.return_value = [
        word.encode() for word in faker.words()
    ]
    return mock_fetcher


@pytest.fixture
def mock_Account_get_fetcher(mocker, mock_fetcher):
    """Mocked :func:`core.models.Account.Account.get_fetcher` method."""
    return mocker.patch(
        "core.models.Account.Account.get_fetcher",
        autospec=True,
        return_value=mock_fetcher,
    )


@pytest.fixture
def spy_Mailbox_create_from_data(mocker):
    """Spy for the :func:`core.models.Account.Mailbox.create_from_data` method."""
    return mocker.spy(Mailbox, "create_from_data")


@pytest.mark.django_db
def test_Account_fields(django_user_model, fake_account):
    """Tests the fields of :class:`core.models.Account.Account`."""
    assert fake_account.mail_address is not None
    assert isinstance(fake_account.mail_address, str)
    assert fake_account.mail_address == ""
    assert fake_account.password is not None
    assert isinstance(fake_account.password, str)
    assert fake_account.mail_host is not None
    assert isinstance(fake_account.mail_host, str)
    assert fake_account.mail_host_port is None
    assert fake_account.protocol is not None
    assert isinstance(fake_account.protocol, str)
    assert any(
        fake_account.protocol == protocol for protocol in EmailProtocolChoices.values
    )
    assert fake_account.timeout is not None
    assert isinstance(fake_account.timeout, int)
    assert fake_account.timeout == 10
    assert fake_account.is_healthy is None
    assert fake_account.is_favorite is False
    assert fake_account.user is not None
    assert isinstance(fake_account.user, django_user_model)
    assert fake_account.updated is not None
    assert isinstance(fake_account.updated, datetime.datetime)
    assert fake_account.created is not None
    assert isinstance(fake_account.created, datetime.datetime)


@pytest.mark.django_db
def test_Account___str__(fake_account):
    """Tests the string representation of :class:`core.models.Account.Account`."""
    assert fake_account.mail_address in str(fake_account)
    assert fake_account.protocol in str(fake_account)


@pytest.mark.django_db
def test_Account_foreign_key_deletion(fake_account):
    """Tests the on_delete foreign key constraint in :class:`core.models.Account.Account`."""

    assert fake_account is not None
    fake_account.user.delete()
    with pytest.raises(Account.DoesNotExist):
        fake_account.refresh_from_db()


@pytest.mark.django_db
def test_Account_unique_constraints(django_user_model):
    """Tests the unique constraints of :class:`core.models.Account.Account`."""

    account_1 = baker.make(
        Account, mail_address="abc123", protocol=EmailProtocolChoices.IMAP
    )
    account_2 = baker.make(
        Account, mail_address="abc123", protocol=EmailProtocolChoices.IMAP
    )
    assert account_1.mail_address == account_2.mail_address
    assert account_1.protocol == account_2.protocol
    assert account_1.user != account_2.user

    user = baker.make(django_user_model)

    account_1 = baker.make(Account, user=user, protocol=EmailProtocolChoices.IMAP)
    account_2 = baker.make(Account, user=user, protocol=EmailProtocolChoices.IMAP)
    assert account_1.mail_address != account_2.mail_address
    assert account_1.protocol == account_2.protocol
    assert account_1.user == account_2.user

    baker.make(
        Account, mail_address="abc123", user=user, protocol=EmailProtocolChoices.IMAP
    )
    with pytest.raises(IntegrityError):
        baker.make(
            Account,
            mail_address="abc123",
            user=user,
            protocol=EmailProtocolChoices.IMAP,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetcher_class",
    [
        (EmailProtocolChoices.IMAP, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
    ],
)
def test_Account_get_fetcher_success(
    mocker, mock_logger, fake_account, protocol, expected_fetcher_class
):
    """Tests :func:`core.models.Account.Account.get_fetcher`
    in case of success.
    """
    mocker.patch(
        f"core.models.Account.{expected_fetcher_class.__name__}.__init__",
        return_value=None,
    )
    fake_account.protocol = protocol

    fetcher = fake_account.get_fetcher()

    assert isinstance(fetcher, expected_fetcher_class)
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Account_get_fetcher_bad_protocol(mock_logger, fake_account):
    """Tests :func:`core.models.Account.Account.get_fetcher`
    in case the account has a bad :attr:`core.models.Account.Account.protocol` field.
    """
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])
    fake_account.protocol = "OTHER"

    with pytest.raises(ValueError, match="OTHER"):
        fake_account.get_fetcher()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetcher_class",
    [
        (EmailProtocolChoices.IMAP, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
    ],
)
def test_Account_get_fetcher_init_failure(
    mocker, mock_logger, fake_account, protocol, expected_fetcher_class
):
    """Tests :func:`core.models.Account.Account.get_fetcher`
    in case the fetcher fails to construct with a :class:`core.utils.fetcher.exceptions.MailAccountError`.
    """
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])
    mocker.patch(
        f"core.models.Account.{expected_fetcher_class.__name__}.__init__",
        side_effect=MailAccountError(Exception()),
    )
    fake_account.protocol = protocol

    with pytest.raises(MailAccountError):
        fake_account.get_fetcher()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetcher_class",
    [
        (EmailProtocolChoices.IMAP, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
    ],
)
def test_Account_get_fetcher_class_success(
    fake_account, mock_logger, protocol, expected_fetcher_class
):
    """Tests :func:`core.models.Account.Account.get_fetcher_class`
    in case of success.
    """
    fake_account.protocol = protocol

    fetcher_class = fake_account.get_fetcher_class()

    assert fetcher_class == expected_fetcher_class
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Account_get_fetcher_class_bad_protocol(fake_account, mock_logger):
    """Tests :func:`core.models.Account.Account.get_fetcher_class`
    in case the account has a bad :attr:`core.models.Account.Account.protocol` field.
    """
    fake_account.is_healthy = True
    fake_account.protocol = "OTHER"
    fake_account.save(update_fields=["is_healthy"])

    with pytest.raises(ValueError, match="OTHER"):
        fake_account.get_fetcher_class()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_Account_test_success(
    fake_account, mock_logger, mock_fetcher, mock_Account_get_fetcher
):
    """Tests :func:`core.models.Account.Account.test`
    in case of success.
    """
    fake_account.is_healthy = False
    fake_account.save(update_fields=["is_healthy"])

    fake_account.test()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is True
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_Account_test_bad_protocol(
    fake_error_message,
    fake_account,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
):
    """Tests :func:`core.models.Account.Account.test`
    in case of the account has a bad :attr:`core.models.Account.Account.protocol` field and raises a :class:`ValueError`.
    """
    mock_Account_get_fetcher.side_effect = ValueError(fake_error_message)

    with pytest.raises(ValueError, match=fake_error_message):
        fake_account.test()

    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_test_failure(
    fake_account, mock_logger, mock_fetcher, mock_Account_get_fetcher
):
    """Tests :func:`core.models.Account.Account.test`
    in case of the test fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_fetcher.test.side_effect = MailAccountError(Exception())
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_account.test()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.test.assert_called_once_with()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_test_get_fetcher_error(
    fake_account, mock_logger, mock_Account_get_fetcher
):
    """Tests :func:`core.models.Account.Account.test`
    in case the :func:`core.models.Account.Account.get_fetcher`
    raises a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError(Exception())
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_account.test()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_Account_get_fetcher.return_value.test.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_update_mailboxes_success(
    fake_account,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    spy_Mailbox_create_from_data,
):
    """Tests :func:`core.models.Account.Account.update_mailboxes`
    in case of success.
    """
    fake_account.is_healthy = False
    fake_account.save(update_fields=["is_healthy"])

    fake_account.update_mailboxes()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is True
    assert fake_account.mailboxes.count() == len(
        mock_fetcher.fetch_mailboxes.return_value
    )
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.fetch_mailboxes.assert_called_once_with()
    assert spy_Mailbox_create_from_data.call_count == len(
        mock_fetcher.fetch_mailboxes.return_value
    )
    mock_logger.info.assert_called()


@pytest.mark.django_db(transaction=True)
def test_Account_update_mailboxes_duplicate(
    fake_account,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    spy_Mailbox_create_from_data,
):
    """Tests :func:`core.models.Account.Account.update_mailboxes`
    in case of a fetched mailbox already being in the db.
    """
    baker.make(Mailbox, account=fake_account, name="INBOX")
    mock_fetcher.fetch_mailboxes.return_value[0] = b"INBOX"

    assert fake_account.mailboxes.count() == 1

    fake_account.update_mailboxes()

    fake_account.refresh_from_db()
    assert fake_account.mailboxes.count() == len(
        mock_fetcher.fetch_mailboxes.return_value
    )
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.fetch_mailboxes.assert_called_once_with()
    assert spy_Mailbox_create_from_data.call_count == len(
        mock_fetcher.fetch_mailboxes.return_value
    )
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_update_mailboxes_failure(
    fake_account,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    spy_Mailbox_create_from_data,
):
    """Tests :func:`core.models.Account.Account.update_mailboxes`
    in case fetching mailboxes fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_fetcher.fetch_mailboxes.side_effect = MailAccountError(Exception())
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_account.update_mailboxes()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is False
    assert fake_account.mailboxes.count() == 0
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.fetch_mailboxes.assert_called_once_with()
    spy_Mailbox_create_from_data.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_update_mailboxes_get_fetcher_error(
    fake_account,
    mock_logger,
    mock_fetcher,
    mock_Account_get_fetcher,
    spy_Mailbox_create_from_data,
):
    """Tests :func:`core.models.Account.Account.update_mailboxes`
    in case :func:`core.models.Account.Account.get_fetcher`
    fails with a :class:`core.utils.fetchers.exceptions.MailAccountError`.
    """
    mock_Account_get_fetcher.side_effect = MailAccountError(Exception())
    fake_account.is_healthy = True
    fake_account.save(update_fields=["is_healthy"])

    with pytest.raises(MailAccountError):
        fake_account.update_mailboxes()

    fake_account.refresh_from_db()
    assert fake_account.is_healthy is True
    assert fake_account.mailboxes.count() == 0
    mock_Account_get_fetcher.assert_called_once_with(fake_account)
    mock_fetcher.fetch_mailboxes.assert_not_called()
    spy_Mailbox_create_from_data.assert_not_called()
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_Account_get_absolute_url(fake_account):
    """Tests :func:`core.models.Account.Account.get_absolute_url`."""
    result = fake_account.get_absolute_url()

    assert result == reverse(
        f"web:{fake_account.BASENAME}-detail",
        kwargs={"pk": fake_account.pk},
    )


@pytest.mark.django_db
def test_Account_get_absolute_edit_url(fake_account):
    """Tests :func:`core.models.Account.Account.get_absolute_edit_url`."""
    result = fake_account.get_absolute_edit_url()

    assert result == reverse(
        f"web:{fake_account.BASENAME}-edit",
        kwargs={"pk": fake_account.pk},
    )


@pytest.mark.django_db
def test_Account_get_absolute_list_url(fake_account):
    """Tests :func:`core.models.Account.Account.get_absolute_list_url`."""
    result = fake_account.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_account.BASENAME}-filter-list",
    )
