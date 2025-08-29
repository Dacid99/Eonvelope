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

"""Test file for the :class:`core.utils.fetchers.IMAP4_SSL_Fetcher`."""

import pytest

from core.constants import EmailProtocolChoices
from core.utils.fetchers import POP3_SSL_Fetcher
from core.utils.fetchers.exceptions import MailAccountError

from .test_IMAP4_SSL_Fetcher import mock_ssl_create_default_context
from .test_POP3Fetcher import mock_logger


@pytest.fixture
def pop3_ssl_mailbox(fake_mailbox):
    fake_mailbox.account.protocol = EmailProtocolChoices.POP3_SSL
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_POP3_SSL(mocker, faker):
    mock_POP3_SSL = mocker.patch(
        "core.utils.fetchers.POP3_SSL_Fetcher.poplib.POP3_SSL", autospec=True
    )
    fake_response = faker.sentence().encode("utf-8")
    mock_POP3_SSL.return_value.user.return_value = b"+OK" + fake_response
    mock_POP3_SSL.return_value.pass_.return_value = b"+OK" + fake_response
    mock_POP3_SSL.return_value.noop.return_value = b"+OK"
    mock_POP3_SSL.return_value.stat.return_value = b"+OK" + fake_response
    mock_POP3_SSL.return_value.list.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3_SSL.return_value.retr.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3_SSL.return_value.quit.return_value = b"+OK" + fake_response
    return mock_POP3_SSL


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mail_host_port, timeout",
    [
        (123, 300),
        (123, None),
        (None, 300),
        (None, None),
    ],
)
def test_POP3Fetcher_connect_to_host_success(
    pop3_ssl_mailbox,
    mock_ssl_create_default_context,
    mock_logger,
    mock_POP3_SSL,
    mail_host_port,
    timeout,
):
    pop3_ssl_mailbox.account.mail_host_port = mail_host_port
    pop3_ssl_mailbox.account.timeout = timeout

    POP3_SSL_Fetcher(pop3_ssl_mailbox.account)

    kwargs = {
        "host": pop3_ssl_mailbox.account.mail_host,
        "context": mock_ssl_create_default_context.return_value,
    }
    if mail_host_port:
        kwargs["port"] = mail_host_port
    if timeout:
        kwargs["timeout"] = timeout
    mock_POP3_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_connect_to_host_exception(
    faker, pop3_ssl_mailbox, mock_ssl_create_default_context, mock_logger, mock_POP3_SSL
):
    fake_error_message = faker.sentence()
    mock_POP3_SSL.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3_SSL_Fetcher(pop3_ssl_mailbox.account)

    kwargs = {
        "host": pop3_ssl_mailbox.account.mail_host,
        "context": mock_ssl_create_default_context.return_value,
    }
    if port := pop3_ssl_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := pop3_ssl_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_POP3_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()
