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

"""Test file for the :class:`core.utils.fetchers.IMAP_SSL_Fetcher`."""


import pytest

from core.constants import EmailProtocolChoices
from core.utils.fetchers.exceptions import MailAccountError
from core.utils.fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher

from .test_IMAPFetcher import FakeIMAP4error, fixture_mock_logger


@pytest.fixture(name="imap_ssl_mailbox")
def fixture_imap_ssl_mailbox(mailbox):
    mailbox.account.protocol = EmailProtocolChoices.IMAP_SSL
    mailbox.account.save(update_fields=["protocol"])
    return mailbox


@pytest.fixture(name="mock_IMAP4_SSL", autouse=True)
def fixture_mock_IMAP4_SSL(mocker, faker):
    mock_IMAP4_SSL = mocker.patch(
        "core.utils.fetchers.IMAP_SSL_Fetcher.imaplib.IMAP4_SSL", autospec=True
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
def test_IMAPFetcher_connectToHost_success(
    imap_ssl_mailbox, mock_logger, mock_IMAP4_SSL
):
    IMAP_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {"host": imap_ssl_mailbox.account.mail_host, "ssl_context": None}
    if port := imap_ssl_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imap_ssl_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_connectToHost_exception(
    imap_ssl_mailbox, mock_logger, mock_IMAP4_SSL
):
    mock_IMAP4_SSL.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAP_SSL_Fetcher(imap_ssl_mailbox.account)

    kwargs = {"host": imap_ssl_mailbox.account.mail_host, "ssl_context": None}
    if port := imap_ssl_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imap_ssl_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4_SSL.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()
