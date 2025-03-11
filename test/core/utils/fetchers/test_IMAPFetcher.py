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

"""Test module for the :class:`IMAPFetcher` class."""

import logging

import pytest
from model_bakery import baker

from core.constants import EmailProtocolChoices
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.fetchers.IMAPFetcher import IMAPFetcher

from ...models.test_MailboxModel import fixture_mailboxModel


class FakeIMAP4error(Exception):
    pass


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    mock_logger = mocker.Mock(spec=logging.Logger)
    mocker.patch(
        "core.utils.fetchers.BaseFetcher.logging.getLogger",
        return_value=mock_logger,
        autospec=True,
    )
    return mock_logger


@pytest.fixture(name="imapMailbox")
def fixture_imapMailbox(mailbox):
    mailbox.account.protocol = EmailProtocolChoices.IMAP
    mailbox.account.save(update_fields=["protocol"])
    return mailbox


@pytest.fixture(name="mock_IMAP4", autouse=True)
def fixture_mock_IMAP4(mocker, faker):
    mock_IMAP4 = mocker.patch(
        "core.utils.fetchers.IMAPFetcher.imaplib.IMAP4", autospec=True
    )
    mock_IMAP4.error = FakeIMAP4error
    fake_response = faker.sentence().encode("utf-8")
    mock_IMAP4.return_value.login.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.noop.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.check.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.list.return_value = ("OK", fake_response.split())
    mock_IMAP4.return_value.select.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.unselect.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.uid.return_value = ("OK", [fake_response, b""])
    mock_IMAP4.return_value.logout.return_value = ("BYE", [fake_response])
    return mock_IMAP4


@pytest.mark.django_db
def test_IMAPFetcher___init___success(mocker, imapMailbox, mock_logger, mock_IMAP4):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")

    result = IMAPFetcher(imapMailbox.account)

    assert result.account == imapMailbox.account
    assert result._mailClient == mock_IMAP4.return_value
    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imapMailbox.account.mail_address, imapMailbox.account.password
    )
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___connectionError(
    mocker, imapMailbox, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___badProtocol(mocker, imapMailbox, mock_logger, mock_IMAP4):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    imapMailbox.account.protocol = EmailProtocolChoices.POP3

    with pytest.raises(ValueError, match="not supported"):
        IMAPFetcher(imapMailbox.account)

    spy_IMAPFetcher_connectToHost.assert_not_called()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___loginError(mocker, imapMailbox, mock_logger, mock_IMAP4):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.return_value.login.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imapMailbox.account.mail_address, imapMailbox.account.password
    )
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___loginBadResponse(
    mocker, imapMailbox, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.return_value.login.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imapMailbox.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imapMailbox.account.mail_address, imapMailbox.account.password
    )
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_connectToHost_success(imapMailbox, mock_logger, mock_IMAP4):
    IMAPFetcher(imapMailbox.account)

    kwargs = {"host": imapMailbox.account.mail_host}
    if port := imapMailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imapMailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_connectToHost_exception(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account)

    kwargs = {"host": imapMailbox.account.mail_host}
    if port := imapMailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imapMailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_success(imapMailbox, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imapMailbox.account).test()

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_badResponse(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.noop.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imapMailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_exception(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.noop.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_success(imapMailbox, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imapMailbox.account).test(imapMailbox)

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        imapMailbox.name, readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_wrongMailbox(imapMailbox, mock_logger, mock_IMAP4):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        IMAPFetcher(imapMailbox.account).test(wrongMailbox)

    mock_IMAP4.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAPFetcher_test_mailbox_badResponse(
    imapMailbox, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
        IMAPFetcher(imapMailbox.account).test(imapMailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            imapMailbox.name, readonly=True
        )
    assert mock_IMAP4.return_value.check.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.check.assert_called_with()
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAPFetcher_test_mailbox_exception(
    imapMailbox, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).side_effect = AssertionError

    with pytest.raises(MailboxError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account).test(imapMailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            imapMailbox.name, readonly=True
        )
    assert mock_IMAP4.return_value.check.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.check.assert_called_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_badResponse_ignored(
    imapMailbox, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    IMAPFetcher(imapMailbox.account).test(imapMailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        imapMailbox.name, readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_exception_ignored(
    imapMailbox, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    IMAPFetcher(imapMailbox.account).test(imapMailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        imapMailbox.name, readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_success(mocker, imapMailbox, mock_logger, mock_IMAP4):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]

    result = IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_once_with(
        imapMailbox.name, readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expectedUidFetchCalls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expectedUidFetchCalls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_wrongMailbox(imapMailbox, mock_logger):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        IMAPFetcher(imapMailbox.account).fetchEmails(wrongMailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_badCriterion(imapMailbox, mock_logger):
    with pytest.raises(ValueError, match="not available via"):
        IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAPFetcher_fetchEmails_badResponse(
    imapMailbox, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
        IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox)

    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            imapMailbox.name, readonly=True
        )

    assert mock_IMAP4.return_value.uid.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.uid.assert_called_with("SEARCH", "ALL")
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAPFetcher_fetchEmails_exception(
    imapMailbox, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).side_effect = AssertionError

    with pytest.raises(MailboxError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox)

    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            imapMailbox.name, readonly=True
        )

    assert mock_IMAP4.return_value.uid.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.uid.assert_called_with("SEARCH", "ALL")
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_badResponse_ignored(
    mocker, imapMailbox, mock_logger, mock_IMAP4
):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    result = IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_once_with(
        imapMailbox.name, readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expectedUidFetchCalls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expectedUidFetchCalls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_exception_ignored(
    mocker, imapMailbox, mock_logger, mock_IMAP4
):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    result = IMAPFetcher(imapMailbox.account).fetchEmails(imapMailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_with(imapMailbox.name, readonly=True)
    assert mock_IMAP4.return_value.uid.call_count == len(expectedUidFetchCalls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expectedUidFetchCalls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_success(imapMailbox, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imapMailbox.account).fetchMailboxes()

    assert result == mock_IMAP4.return_value.list.return_value[1]
    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_badResponse(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.list.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imapMailbox.account).fetchMailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_exception(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.list.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imapMailbox.account).fetchMailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_success(imapMailbox, mock_logger, mock_IMAP4):
    IMAPFetcher(imapMailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_noClient(imapMailbox, mock_logger, mock_IMAP4):
    fetcher = IMAPFetcher(imapMailbox.account)
    fetcher._mailClient = None

    fetcher.close()

    mock_IMAP4.return_value.logout.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_badResponse(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.return_value = ("NO", [b""])

    IMAPFetcher(imapMailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_exception(imapMailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.side_effect = AssertionError

    IMAPFetcher(imapMailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___str__(imapMailbox):
    result = str(IMAPFetcher(imapMailbox.account))

    assert str(imapMailbox.account) in result
    assert IMAPFetcher.__name__ in result


@pytest.mark.django_db
def test_IMAPFetcher_context_manager(imapMailbox, mock_logger, mock_IMAP4):
    with pytest.raises(AssertionError), IMAPFetcher(imapMailbox.account):
        raise AssertionError

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_called()
