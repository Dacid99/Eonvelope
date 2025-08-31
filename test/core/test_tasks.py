# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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
    """Extends :func:`test.models.test_Account.mock_fetcher` to return a test-email from `fetch_emails`."""
    with open(TEST_EMAIL_PARAMETERS[0][0], "br") as test_email_file:
        test_email = test_email_file.read()
    mock_fetcher.fetch_emails.return_value = [test_email]
    return mock_fetcher


@pytest.fixture(autouse=True)
def mock_Account_get_test_email_fetcher(
    mock_Account_get_fetcher, mock_test_email_fetcher
):
    """Patches `core.models.Account.get_fetcher` to return a mocked fetcher."""
    mock_Account_get_fetcher.return_value = mock_test_email_fetcher
    return mock_Account_get_fetcher


@pytest.mark.django_db
def test_fetch_emails_task_success(
    fake_daemon,
    mock_Attachment_save_to_storage,
    mock_Email_save_eml_to_storage,
):
    """Tests :func:`core.tasks.fetch_emails`
    in case of success.
    """
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 1
    assert fake_daemon.is_healthy is True


@pytest.mark.django_db
def test_fetch_emails_task_bad_daemon_uuid(faker, fake_daemon):
    """Tests :func:`core.tasks.fetch_emails`
    in case the given uuid doesn't match any daemon entry.
    """
    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(faker.uuid4())

    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_MailboxError(faker, fake_daemon, mock_test_email_fetcher):
    """Tests :func:`core.tasks.fetch_emails`
    in case of an MailboxError.
    """
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = MailboxError(
        Exception(fake_error_message)
    )

    assert fake_daemon.is_healthy is not True

    with pytest.raises(MailboxError, match=fake_error_message):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.mailbox.is_healthy is False
    assert fake_error_message in fake_daemon.last_error


@pytest.mark.django_db
def test_fetch_emails_task_MailAccountError(
    faker, fake_daemon, mock_test_email_fetcher
):
    """Tests :func:`core.tasks.fetch_emails`
    in case of an MailAccountError.
    """
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = MailAccountError(
        Exception(fake_error_message)
    )

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(MailAccountError, match=fake_error_message):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.mailbox.account.is_healthy is False
    assert fake_error_message in fake_daemon.last_error


@pytest.mark.django_db
def test_fetch_emails_task_unexpected_error(
    faker, fake_daemon, mock_test_email_fetcher
):
    """Tests :func:`core.tasks.fetch_emails`
    in case of an unexpected error.
    """
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = AssertionError(
        fake_error_message
    )

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(AssertionError, match=fake_error_message):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is False
    assert fake_error_message in fake_daemon.last_error


@pytest.mark.django_db
def test_fetch_emails_task_ValueError(faker, fake_daemon, mock_test_email_fetcher):
    """Tests :func:`core.tasks.fetch_emails`
    in case of a ValueError.
    """
    fake_error_message = faker.sentence()
    mock_test_email_fetcher.fetch_emails.side_effect = ValueError(fake_error_message)

    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is not True

    with pytest.raises(ValueError, match=fake_error_message):
        fetch_emails(str(fake_daemon.uuid))

    fake_daemon.refresh_from_db()
    assert fake_daemon.mailbox.emails.count() == 0
    assert fake_daemon.is_healthy is False
    assert fake_error_message in fake_daemon.last_error
