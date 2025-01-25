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


import pytest
import core.utils.mailProcessing
from .models.test_AccountModel import fixture_accountModel
from .models.test_MailboxModel import fixture_mailboxModel
from core.constants import MailFetchingProtocols

@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.utils.fileManagment.logger` of the module."""
    return mocker.patch('core.utils.mailProcessing.logger')

@pytest.mark.django_db
@pytest.mark.parametrize(
    'protocol, expected_call',
    [
        (MailFetchingProtocols.IMAP, 'core.utils.mailProcessing.IMAPFetcher.testAccount'),
        (MailFetchingProtocols.POP3, 'core.utils.mailProcessing.POP3Fetcher.testAccount'),
        (MailFetchingProtocols.IMAP_SSL, 'core.utils.mailProcessing.IMAP_SSL_Fetcher.testAccount'),
        (MailFetchingProtocols.POP3_SSL, 'core.utils.mailProcessing.POP3_SSL_Fetcher.testAccount')
    ]
)
def test_testAccount_success(mocker, mock_logger, account, protocol, expected_call):
    account.protocol = protocol
    mock_testAccount = mocker.patch(expected_call, return_value=1)

    result = core.utils.mailProcessing.testAccount(account)

    assert result == 1
    mock_testAccount.assert_called_once_with(account)
    mock_logger.info.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'protocol, expected_call',
    [
        (MailFetchingProtocols.IMAP, 'core.utils.mailProcessing.IMAPFetcher.testMailbox'),
        (MailFetchingProtocols.POP3, 'core.utils.mailProcessing.POP3Fetcher.testMailbox'),
        (MailFetchingProtocols.IMAP_SSL, 'core.utils.mailProcessing.IMAP_SSL_Fetcher.testMailbox'),
        (MailFetchingProtocols.POP3_SSL, 'core.utils.mailProcessing.POP3_SSL_Fetcher.testMailbox')
    ]
)
def test_testMailbox_success(mocker, mock_logger, mailbox, protocol, expected_call):
    mailbox.account.protocol = protocol
    mock_testAccount = mocker.patch(expected_call, return_value=1)

    result = core.utils.mailProcessing.testMailbox(mailbox)

    assert result == 1
    mock_testAccount.assert_called_once_with(mailbox)
    mock_logger.info.assert_called()


@pytest.mark.django_db
def test_testAccount_failure(mocker, mock_logger, account):
    account.protocol = 'OTHER'

    result = core.utils.mailProcessing.testAccount(account)

    assert result == 3
    account.refresh_from_db()
    assert account.is_healthy is False
    mock_logger.error.assert_called()
