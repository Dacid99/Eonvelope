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
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker

from core.constants import EmailProtocolChoices, MailboxTypeChoices
from core.models import Account, Daemon, Mailbox
from core.utils.fetchers import (
    BaseFetcher,
    ExchangeFetcher,
    IMAP4_SSL_Fetcher,
    IMAP4Fetcher,
    JMAPFetcher,
    POP3_SSL_Fetcher,
    POP3Fetcher,
)
from core.utils.fetchers.exceptions import MailAccountError
from src.core.constants import EmailFetchingCriterionChoices


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
        (word, type_choice)
        for word, type_choice in zip(
            faker.words(),
            faker.random_elements(MailboxTypeChoices.values),
            strict=False,
        )
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
    # ruff: disable[S106]
    account_1 = baker.make(
        Account,
        mail_address="abc123",
        password="passwordlol",
        protocol=EmailProtocolChoices.IMAP4,
    )
    account_2 = baker.make(
        Account,
        mail_address="abc123",
        password="passwordlol",
        protocol=EmailProtocolChoices.IMAP4,
    )
    assert account_1.mail_address == account_2.mail_address
    assert account_1.password == account_2.password
    assert account_1.protocol == account_2.protocol
    assert account_1.user != account_2.user

    user = baker.make(django_user_model)

    account_1 = baker.make(
        Account,
        user=user,
        mail_address="user1@server.com",
        password="qwerty1234",
        protocol=EmailProtocolChoices.EXCHANGE,
    )
    account_2 = baker.make(
        Account,
        user=user,
        mail_address="user2@server.com",
        password="qwerty1234",
        protocol=EmailProtocolChoices.EXCHANGE,
    )
    assert account_1.mail_address != account_2.mail_address
    assert account_1.password == account_2.password
    assert account_1.protocol == account_2.protocol
    assert account_1.user == account_2.user

    account_1 = baker.make(
        Account,
        user=user,
        mail_address="mail@test.org",
        password="abcdef",
        protocol=EmailProtocolChoices.POP3_SSL,
    )
    account_2 = baker.make(
        Account,
        user=user,
        mail_address="mail@test.org",
        password="abcdef",
        protocol=EmailProtocolChoices.POP3,
    )
    assert account_1.mail_address == account_2.mail_address
    assert account_1.password == account_2.password
    assert account_1.protocol != account_2.protocol
    assert account_1.user == account_2.user

    account_1 = baker.make(
        Account,
        user=user,
        mail_address="mail@test.org",
        password="123456",
        protocol=EmailProtocolChoices.JMAP,
    )
    account_2 = baker.make(
        Account,
        user=user,
        mail_address="mail@test.org",
        password="abcdef",
        protocol=EmailProtocolChoices.JMAP,
    )
    assert account_1.mail_address == account_2.mail_address
    assert account_1.password != account_2.password
    assert account_1.protocol == account_2.protocol
    assert account_1.user == account_2.user

    baker.make(
        Account,
        user=user,
        mail_address="abc123",
        password="mypassword",
        protocol=EmailProtocolChoices.IMAP4,
    )
    with pytest.raises(IntegrityError):
        baker.make(
            Account,
            user=user,
            mail_address="abc123",
            password="mypassword",
            protocol=EmailProtocolChoices.IMAP4,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol, expected_fetcher_class",
    [
        (EmailProtocolChoices.IMAP4, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
        (EmailProtocolChoices.JMAP, JMAPFetcher),
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
        (EmailProtocolChoices.IMAP4, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
        (EmailProtocolChoices.JMAP, JMAPFetcher),
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
        (EmailProtocolChoices.IMAP4, IMAP4Fetcher),
        (EmailProtocolChoices.IMAP4_SSL, IMAP4_SSL_Fetcher),
        (EmailProtocolChoices.POP3, POP3Fetcher),
        (EmailProtocolChoices.POP3_SSL, POP3_SSL_Fetcher),
        (EmailProtocolChoices.EXCHANGE, ExchangeFetcher),
        (EmailProtocolChoices.JMAP, JMAPFetcher),
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
    mock_fetcher.fetch_mailboxes.return_value[0] = ("INBOX", "")

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
@pytest.mark.parametrize(
    "protocol",
    [
        EmailProtocolChoices.IMAP4,
        EmailProtocolChoices.IMAP4_SSL,
        EmailProtocolChoices.JMAP,
        EmailProtocolChoices.EXCHANGE,
    ],
)
def test_Account_add_daemons_success(faker, override_config, fake_account, protocol):
    """Tests :func:`core.models.Account.Account.add_daemons`
    in case of success.
    """
    fake_inbox_every = faker.random.randint(1, 100)
    fake_sentbox_every = faker.random.randint(1, 100)
    fake_account.protocol = protocol
    fake_inbox = fake_account.mailboxes.create(
        name="INBOX", type=MailboxTypeChoices.INBOX
    )
    fake_sentbox = fake_account.mailboxes.create(
        name="SENT", type=MailboxTypeChoices.SENT
    )

    assert Daemon.objects.count() == 0
    assert fake_account.mailboxes.count() == 2
    with override_config(
        DEFAULT_INBOX_INTERVAL_EVERY=fake_inbox_every,
        DEFAULT_SENTBOX_INTERVAL_EVERY=fake_sentbox_every,
        DEFAULT_INBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.SEEN,
        DEFAULT_SENTBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.ANNUALLY,
    ):
        fake_account.add_daemons()

    assert Daemon.objects.count() == 2
    assert fake_inbox.daemons.count() == 1
    fake_inbox_daemon = fake_inbox.daemons.first()
    assert fake_inbox_daemon.interval.period == IntervalSchedule.SECONDS
    assert fake_inbox_daemon.interval.every == fake_inbox_every
    assert fake_inbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.SEEN
    assert fake_inbox_daemon.fetching_criterion_arg == ""
    assert fake_sentbox.daemons.count() == 1
    fake_sentbox_daemon = fake_sentbox.daemons.first()
    assert fake_sentbox_daemon.interval.period == IntervalSchedule.HOURS
    assert fake_sentbox_daemon.interval.every == fake_sentbox_every
    assert (
        fake_sentbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.ANNUALLY
    )
    assert fake_sentbox_daemon.fetching_criterion_arg == ""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "protocol", [EmailProtocolChoices.POP3, EmailProtocolChoices.POP3_SSL]
)
def test_Account_add_daemons_success_pop(
    faker, override_config, fake_account, protocol
):
    """Tests :func:`core.models.Account.Account.add_daemons`
    in case of success with a POP account.
    """
    fake_inbox_every = faker.random.randint(1, 100)
    fake_sentbox_every = faker.random.randint(1, 100)
    fake_account.protocol = protocol
    fake_inbox = fake_account.mailboxes.create(
        name="INBOX", type=MailboxTypeChoices.INBOX
    )
    fake_sentbox = fake_account.mailboxes.create(
        name="SENT", type=MailboxTypeChoices.SENT
    )

    assert Daemon.objects.count() == 0
    assert fake_account.mailboxes.count() == 2

    with override_config(
        DEFAULT_INBOX_INTERVAL_EVERY=fake_inbox_every,
        DEFAULT_SENTBOX_INTERVAL_EVERY=fake_sentbox_every,
    ):
        fake_account.add_daemons()

    assert Daemon.objects.count() == 2
    assert fake_inbox.daemons.count() == 1
    fake_inbox_daemon = fake_inbox.daemons.first()
    assert fake_inbox_daemon.interval.period == IntervalSchedule.SECONDS
    assert fake_inbox_daemon.interval.every == fake_inbox_every
    assert fake_inbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.ALL
    assert fake_inbox_daemon.fetching_criterion_arg == ""
    assert fake_sentbox.daemons.count() == 1
    fake_sentbox_daemon = fake_sentbox.daemons.first()
    assert fake_sentbox_daemon.interval.period == IntervalSchedule.HOURS
    assert fake_sentbox_daemon.interval.every == fake_sentbox_every
    assert fake_inbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.ALL
    assert fake_inbox_daemon.fetching_criterion_arg == ""


@pytest.mark.django_db
def test_Account_add_daemons_success_unavailable_criterion_config(
    faker, override_config, fake_account
):
    """Tests :func:`core.models.Account.Account.add_daemons`
    in case of an unavailable criterion configuration.
    """
    fake_inbox_every = faker.random.randint(1, 100)
    fake_sentbox_every = faker.random.randint(1, 100)
    fake_account.protocol = EmailProtocolChoices.EXCHANGE
    fake_inbox = fake_account.mailboxes.create(
        name="INBOX", type=MailboxTypeChoices.INBOX
    )
    fake_sentbox = fake_account.mailboxes.create(
        name="SENT", type=MailboxTypeChoices.SENT
    )

    assert Daemon.objects.count() == 0
    assert fake_account.mailboxes.count() == 2

    with override_config(
        DEFAULT_INBOX_INTERVAL_EVERY=fake_inbox_every,
        DEFAULT_SENTBOX_INTERVAL_EVERY=fake_sentbox_every,
        DEFAULT_INBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.KEYWORD,
        DEFAULT_SENTBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.RECENT,
    ):
        fake_account.add_daemons()

    assert Daemon.objects.count() == 2
    assert fake_inbox.daemons.count() == 1
    fake_inbox_daemon = fake_inbox.daemons.first()
    assert fake_inbox_daemon.interval.period == IntervalSchedule.SECONDS
    assert fake_inbox_daemon.interval.every == fake_inbox_every
    assert fake_inbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.UNSEEN
    assert fake_inbox_daemon.fetching_criterion_arg == ""
    assert fake_sentbox.daemons.count() == 1
    fake_sentbox_daemon = fake_sentbox.daemons.first()
    assert fake_sentbox_daemon.interval.period == IntervalSchedule.HOURS
    assert fake_sentbox_daemon.interval.every == fake_sentbox_every
    assert fake_sentbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.DAILY
    assert fake_sentbox_daemon.fetching_criterion_arg == ""


@pytest.mark.django_db
def test_Account_add_daemons_twice(faker, override_config, fake_account):
    """Tests :func:`core.models.Account.Account.add_daemons`
    in case its called more than once.
    """
    fake_inbox_every = faker.random.randint(1, 100)
    fake_sentbox_every = faker.random.randint(1, 100)
    fake_inbox = fake_account.mailboxes.create(
        name="INBOX", type=MailboxTypeChoices.INBOX
    )
    fake_sentbox = fake_account.mailboxes.create(
        name="SENT", type=MailboxTypeChoices.SENT
    )

    assert Daemon.objects.count() == 0
    assert fake_account.mailboxes.count() == 2
    with override_config(
        DEFAULT_INBOX_INTERVAL_EVERY=fake_inbox_every,
        DEFAULT_SENTBOX_INTERVAL_EVERY=fake_sentbox_every,
        DEFAULT_INBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.SEEN,
        DEFAULT_SENTBOX_FETCHING_CRITERION=EmailFetchingCriterionChoices.ANNUALLY,
    ):
        fake_account.add_daemons()
        fake_account.add_daemons()

    assert Daemon.objects.count() == 2
    assert fake_inbox.daemons.count() == 1
    fake_inbox_daemon = fake_inbox.daemons.first()
    assert fake_inbox_daemon.interval.period == IntervalSchedule.SECONDS
    assert fake_inbox_daemon.interval.every == fake_inbox_every
    assert fake_inbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.SEEN
    assert fake_inbox_daemon.fetching_criterion_arg == ""
    assert fake_sentbox.daemons.count() == 1
    fake_sentbox_daemon = fake_sentbox.daemons.first()
    assert fake_sentbox_daemon.interval.period == IntervalSchedule.HOURS
    assert fake_sentbox_daemon.interval.every == fake_sentbox_every
    assert (
        fake_sentbox_daemon.fetching_criterion == EmailFetchingCriterionChoices.ANNUALLY
    )
    assert fake_sentbox_daemon.fetching_criterion_arg == ""


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mail_address, user_username, mail_host , expected_address",
    [
        ("no_at", "someone", "stalwart.tld", "no_at@stalwart.tld"),
        ("", "admin", "iloveeonvelope.org", "admin@iloveeonvelope.org"),
        ("valid@mail.address", "server.com", "standard", "valid@mail.address"),
    ],
)
def test_Account_complete_mail_address(
    fake_account, mail_address, user_username, mail_host, expected_address
):
    """Tests the complete_mail_address property of :class:`core.models.Account`
    for all relevant cases.
    """
    fake_account.mail_address = mail_address
    fake_account.mail_host = mail_host
    fake_account.user.username = user_username

    result = fake_account.complete_mail_address

    assert result == expected_address
    assert "@" in result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mail_host, mail_host_port, expected_address",
    [
        ("stalwart.tld", "433", "stalwart.tld:433"),
        ("iloveeonvelope.org", None, "iloveeonvelope.org"),
    ],
)
def test_Account_mail_host_address(
    fake_account, mail_host, mail_host_port, expected_address
):
    """Tests the mail_host_address property of :class:`core.models.Account`
    for all relevant cases.
    """
    fake_account.mail_host = mail_host
    fake_account.mail_host_port = mail_host_port

    result = fake_account.mail_host_address

    assert result == expected_address


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
