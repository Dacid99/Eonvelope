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

"""Test file for the :class:`core.utils.fetchers.IMAP4_SSL_Fetcher`."""

import ssl

import pytest

from core.constants import EmailProtocolChoices
from core.utils.fetchers import POP3_SSL_Fetcher
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture
def pop3_ssl_mailbox(fake_mailbox):
    """Extends :func:`test.conftest.fake_mailbox` to have POP3_SSL as protocol."""
    fake_mailbox.account.protocol = EmailProtocolChoices.POP3_SSL
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_POP3_SSL(mocker, faker):
    """Mocks an :class:`poplib.POP3_SSL` with all positive method responses."""
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
    "mail_host_port",
    [
        123,
        None,
    ],
)
@pytest.mark.parametrize("config_allow_insecure", [True, False])
@pytest.mark.parametrize("account_allow_insecure", [True, False])
def test_POP3Fetcher_connect_to_host__success(
    override_config,
    pop3_ssl_mailbox,
    mock_ssl_create_default_context,
    mock_logger,
    mock_POP3_SSL,
    account_allow_insecure,
    config_allow_insecure,
    mail_host_port,
):
    """Tests :func:`core.utils.fetchers.POP3_SSL_Fetcher.connect_to_host`
    in case of success.
    """
    pop3_ssl_mailbox.account.mail_host_port = mail_host_port
    pop3_ssl_mailbox.account.allow_insecure_connection = account_allow_insecure

    with override_config(ALLOW_INSECURE_CONNECTIONS=config_allow_insecure):
        result = POP3_SSL_Fetcher(pop3_ssl_mailbox.account)

    kwargs = {
        "host": pop3_ssl_mailbox.account.mail_host,
        "timeout": pop3_ssl_mailbox.account.timeout,
        "context": mock_ssl_create_default_context.return_value,
    }
    if mail_host_port:
        kwargs["port"] = mail_host_port
    assert result._mail_client == mock_POP3_SSL.return_value
    mock_POP3_SSL.assert_called_with(**kwargs)
    mock_ssl_create_default_context.assert_called_once_with(
        purpose=(
            ssl.Purpose.CLIENT_AUTH
            if account_allow_insecure and config_allow_insecure
            else ssl.Purpose.SERVER_AUTH
        )
    )
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_connect_to_host__exception(
    fake_error_message,
    pop3_ssl_mailbox,
    mock_ssl_create_default_context,
    mock_logger,
    mock_POP3_SSL,
):
    """Tests :func:`core.utils.fetchers.POP3_SSL_Fetcher.connect_to_host`
    in case of an error.
    """
    mock_POP3_SSL.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
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
