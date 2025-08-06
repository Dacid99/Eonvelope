import logging

import pytest

from core.tasks import fetch_emails
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from test.conftest import TEST_EMAIL_PARAMETERS

from .models.test_Account import mock_Account_get_fetcher, mock_fetcher
from .models.test_Attachment import mock_Attachment_save_to_storage
from .models.test_Email import mock_Email_save_eml_to_storage


@pytest.fixture(autouse=True)
def mock_get_daemon_logger(mocker, fake_daemon):
    mock_getLogger = mocker.patch("core.tasks.logging.getLogger")
    mock_getLogger.return_value = mocker.MagicMock(spec=logging.Logger)
    return mock_getLogger


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
    mock_get_daemon_logger,
    mock_Attachment_save_to_storage,
    mock_Email_save_eml_to_storage,
):
    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(str(fake_daemon.uuid))

    mock_get_daemon_logger.assert_called_with(str(fake_daemon.uuid))
    mock_get_daemon_logger.return_value.info.assert_called()
    assert fake_daemon.mailbox.emails.count() == 1


@pytest.mark.django_db
def test_fetch_emails_task_bad_daemon_uuid(
    faker,
    fake_daemon,
):
    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(faker.uuid4())

    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_MailboxError(
    fake_daemon, mock_test_email_fetcher, mock_get_daemon_logger
):
    mock_test_email_fetcher.fetch_emails.side_effect = MailboxError

    fetch_emails(str(fake_daemon.uuid))

    mock_get_daemon_logger.return_value.exception.assert_called()
    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_MailAccountError(
    fake_daemon, mock_test_email_fetcher, mock_get_daemon_logger
):
    mock_test_email_fetcher.fetch_emails.side_effect = MailAccountError

    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(str(fake_daemon.uuid))

    mock_get_daemon_logger.return_value.exception.assert_called()
    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_unexpected_error(
    fake_daemon, mock_test_email_fetcher, mock_get_daemon_logger
):
    mock_test_email_fetcher.fetch_emails.side_effect = AssertionError

    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(str(fake_daemon.uuid))

    mock_get_daemon_logger.return_value.exception.assert_called()
    assert fake_daemon.mailbox.emails.count() == 0


@pytest.mark.django_db
def test_fetch_emails_task_ValueError(
    fake_daemon, mock_test_email_fetcher, mock_get_daemon_logger
):
    mock_test_email_fetcher.fetch_emails.side_effect = ValueError

    assert fake_daemon.mailbox.emails.count() == 0

    fetch_emails(str(fake_daemon.uuid))

    mock_get_daemon_logger.return_value.exception.assert_called()
    assert fake_daemon.mailbox.emails.count() == 0
