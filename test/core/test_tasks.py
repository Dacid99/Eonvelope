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

"""Test file for :mod:`core.tasks`."""

import pytest

from core.tasks import fetch_emails
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from test.conftest import TEST_EMAIL_PARAMETERS

from .models.test_Account import mock_Account_get_fetcher, mock_fetcher
from .models.test_Attachment import mock_Attachment_save_to_storage
from .models.test_Email import mock_Email_save_eml_to_storage


@pytest.fixture
def mock_test_email_fetcher(mock_fetcher):
    with open(TEST_EMAIL_PARAMETERS[0][0], "br") as f:
        test_email = f.read()
    mock_fetcher.fetch_emails.return_value = [test_email]
    return mock_fetcher


@pytest.fixture(autouse=True)
def mock_Account_get_test_email_fetcher(
    mock_Account_get_fetcher, mock_test_email_fetcher
):
    mock_Account_get_fetcher.return_value = mock_test_email_fetcher
    return mock_Account_get_fetcher


@pytest.mark.django_db
def test_fetch_emails_task_success(
    fake_daemon,
    mock_Attachment_save_to_storage,
    mock_Email_save_eml_to_storage,
):
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 1
    assert fake_daemon.is_healthy is True


@pytest.mark.django_db
def test_fetch_emails_task_bad_daemon_uuid(faker, fake_daemon):
    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(faker.uuid4())

    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_MailboxError(faker, fake_daemon, mock_test_email_fetcher):
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = MailboxError(fake_error_message)

    assert fake_daemon.is_healthy is not True

    with pytest.raises(MailboxError):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.mailbox.is_healthy is False
    assert fake_daemon.last_error == fake_error_message


@pytest.mark.django_db
def test_fetch_emails_task_MailAccountError(
    faker, fake_daemon, mock_test_email_fetcher
):
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = MailAccountError(
        fake_error_message
    )

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(MailAccountError):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.mailbox.account.is_healthy is False
    assert fake_daemon.last_error == fake_error_message


@pytest.mark.django_db
def test_fetch_emails_task_unexpected_error(
    faker, fake_daemon, mock_test_email_fetcher
):
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = AssertionError(
        fake_error_message
    )

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(AssertionError):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is False
    assert fake_daemon.last_error == fake_error_message


@pytest.mark.django_db
def test_fetch_emails_task_ValueError(faker, fake_daemon, mock_test_email_fetcher):
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = ValueError(fake_error_message)

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(ValueError):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is False
    assert fake_daemon.last_error == fake_error_message
