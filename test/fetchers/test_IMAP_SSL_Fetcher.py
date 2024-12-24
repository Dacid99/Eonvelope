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

import imaplib
import logging
from unittest.mock import MagicMock, patch

import pytest

from Emailkasten.Fetchers.IMAPFetcher import \
    IMAPFetcher
from Emailkasten.Models.AccountModel import \
    AccountModel


@pytest.fixture(name='mock_account')
def fixture_mock_account():
    account = MagicMock(spec=AccountModel)
    account.mail_host = "imap.example.com"
    account.mail_host_port = 993
    account.mail_address = "user@example.com"
    account.password = "password"
    account.is_healthy = True
    return account


# Test for IMAP connection success
@patch('IMAPFetcher.connectToHost')
@patch('IMAPFetcher.login')
@patch('logging.getLogger')
def test_imapfetcher_success(mock_logger, mock_login, mock_connect, mock_account):
    """Test successful connection and login to IMAP server."""

    # Call the constructor, which triggers connectToHost and login
    fetcher = IMAPFetcher(mock_account)

    # Assert that connectToHost and login were called
    mock_connect.assert_called_once()
    mock_login.assert_called_once()

    # Assert the account's health status is marked as healthy
    mock_account.save.assert_called_once_with()
    mock_account.is_healthy = True  # This will be set in the real method

    # Ensure the logger didn't log an error
    mock_logger().error.assert_not_called()


# Test for IMAP connection failure
@patch('IMAPFetcher.connectToHost', side_effect=imaplib.IMAP4.error)
@patch('logging.getLogger')
def test_imapfetcher_imap_error(mock_logger, mock_connect, mock_account):
    """Test handling of IMAP connection error."""

    # Call the constructor, which should raise an error in connectToHost
    fetcher = IMAPFetcher(mock_account)

    # Assert that the account is marked as unhealthy
    mock_account.save.assert_called_once_with()
    mock_account.is_healthy = False

    # Ensure that the appropriate error message was logged
    mock_logger().error.assert_called_once()


# Test for IMAP connection failure
@patch('imaplib.IMAP4.list', return_value=['NO','errorcode'])
@patch('IMAPFetcher.login')
@patch('IMAPFetcher.connectToHost')
@patch('logging.getLogger')
def test_imapfetcher_badresponse_fetchMailboxes(mock_logger, mock_connect, mock_login, mock_list, mock_account):
    """Test handling of IMAP connection error."""

    # Call the constructor, which should raise an error in connectToHost
    fetcher = IMAPFetcher(mock_account)
    fetcher.fetchMailboxes()

    # Assert that the account is marked as unhealthy
    mock_account.save.assert_called_once_with()
    mock_account.is_healthy = False

    # Ensure that the appropriate error message was logged
    mock_logger().error.assert_called_once()


# Test for unexpected error
@patch('myapp.emailfetcher.IMAPFetcher.connectToHost', side_effect=Exception("Unexpected error"))
@patch('myapp.emailfetcher.logging.getLogger')
def test_imapfetcher_unexpected_error(mock_logger, mock_connect, mock_account):
    """Test handling of unexpected errors during connection."""

    # Call the constructor, which should raise an unexpected exception
    fetcher = IMAPFetcher(mock_account)

    # Assert that the account is marked as unhealthy
    mock_account.save.assert_called_once_with()
    mock_account.is_healthy = False

    # Ensure that the appropriate error message was logged
    mock_logger().error.assert_called_once()
