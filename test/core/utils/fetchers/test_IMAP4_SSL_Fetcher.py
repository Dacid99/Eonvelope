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

"""Test file for the :class:`core.utils.fetchers.IMAP4_SSL_Fetcher`."""


import pytest

from core.constants import EmailProtocolChoices
from core.utils.fetchers import IMAP4_SSL_Fetcher
from core.utils.fetchers.exceptions import MailAccountError

from .test_IMAP4Fetcher import FakeIMAP4error, mock_logger


@pytest.fixture
def imap_ssl_mailbox(fake_mailbox):
    fake_mailbox.account.protocol = EmailProtocolChoices.IMAP4_SSL
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_IMAP4_SSL(mocker, faker):
    mock_IMAP4_SSL = mocker.patch(
        "core.utils.fetchers.IMAP4_SSL_Fetcher.imaplib.IMAP4_SSL", autospec=True
    )
    mock_IMAP4_SSL.error = FakeIMAP4error
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
    "mail_host_port, timeout",
    [
        (123, 300),
        (123, None),
        (None, 300),
        (None, None),
    ],
)
def test_IMAP4Fetcher_connect_to_host_success(
    imap_ssl_mailbox, mock_logger, mock_IMAP4_SSL, mail_host_port, timeout
):
    imap_ssl_mailbox.account.mail_host_port = mail_host_port
    imap_ssl_mailbox.account.timeout = timeout

    IMAP4_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {"host": imap_ssl_mailbox.account.mail_host, "ssl_context": None}
    if mail_host_port:
        kwargs["port"] = mail_host_port
    if timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_connect_to_host_exception(
    imap_ssl_mailbox, mock_logger, mock_IMAP4_SSL
):
    mock_IMAP4_SSL.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAP4_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {"host": imap_ssl_mailbox.account.mail_host, "ssl_context": None}
    if port := imap_ssl_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imap_ssl_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()
