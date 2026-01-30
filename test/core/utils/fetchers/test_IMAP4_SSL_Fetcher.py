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
from core.utils.fetchers import IMAP4_SSL_Fetcher
from core.utils.fetchers.exceptions import MailAccountError

from .test_IMAP4Fetcher import FakeIMAP4Error


@pytest.fixture
def imap_ssl_mailbox(fake_mailbox):
    """Extends :func:`test.conftest.fake_mailbox` to have IMAP4_SSL as protocol."""
    fake_mailbox.account.protocol = EmailProtocolChoices.IMAP4_SSL
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_IMAP4_SSL(mocker, faker):
    """Mocks an :class:`imaplib.IMAP4_SSL` with all positive method responses."""
    mock_IMAP4_SSL = mocker.patch(
        "core.utils.fetchers.IMAP4_SSL_Fetcher.imaplib.IMAP4_SSL", autospec=True
    )
    mock_IMAP4_SSL.error = FakeIMAP4Error
    fake_response = faker.sentence().encode("utf-8")
    mock_IMAP4_SSL.return_value.login.return_value = ("OK", [fake_response])
    mock_IMAP4_SSL.return_value.noop.return_value = ("OK", [fake_response])
    mock_IMAP4_SSL.return_value.check.return_value = ("OK", [fake_response])
    mock_IMAP4_SSL.return_value.list.return_value = ("OK", fake_response.split())
    mock_IMAP4_SSL.return_value.select.return_value = ("OK", [fake_response])
    mock_IMAP4_SSL.return_value.unselect.return_value = ("OK", [fake_response])
    mock_IMAP4_SSL.return_value.uid.return_value = ("OK", [fake_response, b""])
    mock_IMAP4_SSL.return_value.logout.return_value = ("BYE", [fake_response])
    return mock_IMAP4_SSL


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
def test_IMAP4Fetcher_connect_to_host__success(
    override_config,
    imap_ssl_mailbox,
    mock_ssl_create_default_context,
    mock_logger,
    mock_IMAP4_SSL,
    account_allow_insecure,
    config_allow_insecure,
    mail_host_port,
):
    """Tests :func:`core.utils.fetchers.IMAP4_SSL_Fetcher.connect_to_host`
    in case of success.
    """
    imap_ssl_mailbox.account.mail_host_port = mail_host_port
    imap_ssl_mailbox.account.allow_insecure_connection = account_allow_insecure

    with override_config(ALLOW_INSECURE_CONNECTIONS=config_allow_insecure):
        result = IMAP4_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {
        "host": imap_ssl_mailbox.account.mail_host,
        "ssl_context": mock_ssl_create_default_context.return_value,
        "timeout": imap_ssl_mailbox.account.timeout,
    }
    if mail_host_port:
        kwargs["port"] = mail_host_port
    assert result._mail_client == mock_IMAP4_SSL.return_value
    mock_ssl_create_default_context.assert_called_once_with(
        purpose=(
            ssl.Purpose.CLIENT_AUTH
            if account_allow_insecure and config_allow_insecure
            else ssl.Purpose.SERVER_AUTH
        )
    )
    mock_IMAP4_SSL.assert_called_once_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_connect_to_host__exception(
    fake_error_message,
    imap_ssl_mailbox,
    mock_ssl_create_default_context,
    mock_logger,
    mock_IMAP4_SSL,
):
    """Tests :func:`core.utils.fetchers.IMAP4_SSL_Fetcher.connect_to_host`
    in case of an error.
    """
    mock_IMAP4_SSL.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {
        "host": imap_ssl_mailbox.account.mail_host,
        "ssl_context": mock_ssl_create_default_context.return_value,
    }
    if imap_ssl_mailbox.account.mail_host_port:
        kwargs["port"] = imap_ssl_mailbox.account.mail_host_port
    if imap_ssl_mailbox.account.timeout:
        kwargs["timeout"] = imap_ssl_mailbox.account.timeout
    mock_IMAP4_SSL.assert_called_once_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()
