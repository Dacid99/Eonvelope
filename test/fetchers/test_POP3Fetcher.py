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

"""Test module for the :class:`POP3Fetcher` class."""

import logging

import pytest
from model_bakery import baker

from core.constants import EmailProtocolChoices
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError
from core.utils.fetchers.POP3Fetcher import POP3Fetcher

from ..models.test_MailboxModel import fixture_mailboxModel


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    mock_logger = mocker.Mock(spec=logging.Logger)
    mocker.patch(
        "core.utils.fetchers.BaseFetcher.logging.getLogger",
        return_value=mock_logger,
    )
    return mock_logger


@pytest.fixture(name="pop3mailbox")
def fixture_pop3mailbox(mailbox):
    mailbox.account.protocol = EmailProtocolChoices.POP3
    mailbox.account.save(update_fields=["protocol"])
    return mailbox


@pytest.fixture(name="mock_POP3", autouse=True)
def fixture_mock_POP3(mocker, faker):
    mock_POP3 = mocker.patch(
        "core.utils.fetchers.POP3Fetcher.poplib.POP3", autospec=True
    )
    fake_response = faker.sentence().encode("utf-8")
    mock_POP3.return_value.user.return_value = b"+OK" + fake_response
    mock_POP3.return_value.pass_.return_value = b"+OK" + fake_response
    mock_POP3.return_value.noop.return_value = b"+OK"
    mock_POP3.return_value.stat.return_value = b"+OK" + fake_response
    mock_POP3.return_value.list.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3.return_value.retr.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3.return_value.quit.return_value = b"+OK" + fake_response
    return mock_POP3


@pytest.mark.django_db
def test_POP3Fetcher___init___success(mocker, pop3mailbox, mock_logger, mock_POP3):
    spy_POP3Fetcher_connectToHost = mocker.spy(POP3Fetcher, "connectToHost")

    result = POP3Fetcher(pop3mailbox.account)

    assert result.account == pop3mailbox.account
    assert result._mailClient == mock_POP3.return_value
    spy_POP3Fetcher_connectToHost.assert_called_once()
    mock_POP3.return_value.user.assert_called_once_with(
        pop3mailbox.account.mail_address
    )
    mock_POP3.return_value.pass_.assert_called_once_with(pop3mailbox.account.password)
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher___init___connectionError(
    mocker, pop3mailbox, mock_logger, mock_POP3
):
    spy_POP3Fetcher_connectToHost = mocker.spy(POP3Fetcher, "connectToHost")
    mock_POP3.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account)

    spy_POP3Fetcher_connectToHost.assert_called_once()
    mock_POP3.return_value.user.assert_not_called()
    mock_POP3.return_value.pass_.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher___init___badProtocol(mocker, pop3mailbox, mock_logger, mock_POP3):
    spy_POP3Fetcher_connectToHost = mocker.spy(POP3Fetcher, "connectToHost")
    pop3mailbox.account.protocol = EmailProtocolChoices.IMAP

    with pytest.raises(ValueError, match="not supported"):
        POP3Fetcher(pop3mailbox.account)

    spy_POP3Fetcher_connectToHost.assert_not_called()
    mock_POP3.return_value.user.assert_not_called()
    mock_POP3.return_value.pass_.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("user", (1, 0)), ("pass_", (1, 1))]
)
def test_POP3Fetcher___init___exception(
    mocker, pop3mailbox, mock_logger, mock_POP3, raisingFunction, expectedCalls
):
    spy_POP3Fetcher_connectToHost = mocker.spy(POP3Fetcher, "connectToHost")
    getattr(mock_POP3.return_value, raisingFunction).side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account)

    spy_POP3Fetcher_connectToHost.assert_called_once()
    assert mock_POP3.return_value.user.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_POP3.return_value.user.assert_called_with(pop3mailbox.account.mail_address)
    assert mock_POP3.return_value.pass_.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_POP3.return_value.pass_.assert_called_with(pop3mailbox.account.password)
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("user", (1, 0)), ("pass_", (1, 1))]
)
def test_POP3Fetcher___init___badResponse(
    mocker, pop3mailbox, mock_logger, mock_POP3, raisingFunction, expectedCalls
):
    spy_POP3Fetcher_connectToHost = mocker.spy(POP3Fetcher, "connectToHost")
    getattr(mock_POP3.return_value, raisingFunction).return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3mailbox.account)

    spy_POP3Fetcher_connectToHost.assert_called_once()
    assert mock_POP3.return_value.user.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_POP3.return_value.user.assert_called_with(pop3mailbox.account.mail_address)
    assert mock_POP3.return_value.pass_.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_POP3.return_value.pass_.assert_called_with(pop3mailbox.account.password)
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_connectToHost_success(pop3mailbox, mock_logger, mock_POP3):
    POP3Fetcher(pop3mailbox.account)

    kwargs = {"host": pop3mailbox.account.mail_host}
    if port := pop3mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := pop3mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_POP3.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_connectToHost_exception(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account)

    kwargs = {"host": pop3mailbox.account.mail_host}
    if port := pop3mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := pop3mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_POP3.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_success(pop3mailbox, mock_logger, mock_POP3):
    result = POP3Fetcher(pop3mailbox.account).test()

    assert result is None
    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_badResponse(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.noop.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3mailbox.account).test()

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_exception(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.noop.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account).test()

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_success(pop3mailbox, mock_logger, mock_POP3):
    result = POP3Fetcher(pop3mailbox.account).test(pop3mailbox)

    assert result is None
    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.stat.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_wrongMailbox(pop3mailbox, mock_logger, mock_POP3):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        POP3Fetcher(pop3mailbox.account).test(wrongMailbox)

    mock_POP3.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_badResponse(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.stat.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3mailbox.account).test(pop3mailbox)

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.stat.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_exception(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.stat.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account).test(pop3mailbox)

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.stat.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_success(mocker, pop3mailbox, mock_logger, mock_POP3):
    expectedRetrCalls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]

    result = POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox)

    assert result == [b"\n".join(mock_POP3.return_value.retr.return_value[1])] * len(
        expectedRetrCalls
    )
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expectedRetrCalls)
    mock_POP3.return_value.retr.assert_has_calls(expectedRetrCalls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_wrongMailbox(pop3mailbox, mock_logger):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        POP3Fetcher(pop3mailbox.account).fetchEmails(wrongMailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_badCriterion(pop3mailbox, mock_logger):
    with pytest.raises(ValueError, match="not available via"):
        POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_badResponse(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.list.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox)

    mock_POP3.return_value.list.assert_called_once_with()
    mock_POP3.return_value.retr.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_exception(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.list.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox)

    mock_POP3.return_value.list.assert_called_once_with()
    mock_POP3.return_value.retr.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_badResponse_ignored(
    mocker, pop3mailbox, mock_logger, mock_POP3
):
    expectedRetrCalls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]
    mock_POP3.return_value.retr.return_value = b"+NO"

    result = POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox)

    assert result == []
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expectedRetrCalls)
    mock_POP3.return_value.retr.assert_has_calls(expectedRetrCalls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchEmails_exception_ignored(
    mocker, pop3mailbox, mock_logger, mock_POP3
):
    expectedRetrCalls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]
    mock_POP3.return_value.retr.side_effect = AssertionError

    result = POP3Fetcher(pop3mailbox.account).fetchEmails(pop3mailbox)

    assert result == []
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expectedRetrCalls)
    mock_POP3.return_value.retr.assert_has_calls(expectedRetrCalls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetchMailboxes(pop3mailbox):
    result = POP3Fetcher(pop3mailbox.account).fetchMailboxes()

    assert result == [b"INBOX"]


@pytest.mark.django_db
def test_POP3Fetcher_close_success(pop3mailbox, mock_logger, mock_POP3):
    POP3Fetcher(pop3mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_close_noClient(pop3mailbox, mock_logger, mock_POP3):
    fetcher = POP3Fetcher(pop3mailbox.account)
    fetcher._mailClient = None

    fetcher.close()

    mock_POP3.return_value.quit.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_close_badResponse(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.quit.return_value = b"+NO"

    POP3Fetcher(pop3mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_close_exception(pop3mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.quit.side_effect = AssertionError

    POP3Fetcher(pop3mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher___str__(pop3mailbox):
    result = str(POP3Fetcher(pop3mailbox.account))

    assert str(pop3mailbox.account) in result
    assert POP3Fetcher.__name__ in result


@pytest.mark.django_db
def test_POP3Fetcher_context_manager(pop3mailbox, mock_logger, mock_POP3):
    with pytest.raises(AssertionError), POP3Fetcher(pop3mailbox.account):
        raise AssertionError

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.error.assert_called()
