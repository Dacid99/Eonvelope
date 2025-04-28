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

import datetime
import logging
from imaplib import Time2Internaldate

import pytest
from freezegun import freeze_time
from imap_tools.imap_utf7 import utf7_encode
from model_bakery import baker

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.fetchers.IMAPFetcher import IMAPFetcher


class FakeIMAP4error(Exception):
    pass


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    mock_logger = mocker.Mock(spec=logging.Logger)
    mocker.patch(
        "core.utils.fetchers.BaseFetcher.logging.getLogger",
        return_value=mock_logger,
        autospec=True,
    )
    return mock_logger


@pytest.fixture
def imap_mailboxModel(mailboxModel):
    mailboxModel.account.protocol = EmailProtocolChoices.IMAP
    mailboxModel.account.save(update_fields=["protocol"])
    return mailboxModel


@pytest.fixture(autouse=True)
def mock_IMAP4(mocker, faker):
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


@pytest.mark.parametrize(
    "criterionName, expectedTimeDelta",
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_IMAPFetcher_makeFetchingCriterion_dateCriterion(
    faker, criterionName, expectedTimeDelta
):
    fake_datetime = faker.date_time_this_decade(tzinfo=faker.pytimezone())
    expectedCriterion = f"SENTSINCE {Time2Internaldate(fake_datetime - expectedTimeDelta).split(" ")[
        0
    ].strip('" ')}"

    with freeze_time(fake_datetime):
        result = IMAPFetcher.makeFetchingCriterion(criterionName)

    assert result == expectedCriterion


@pytest.mark.parametrize(
    "criterionName, expectedResult",
    [
        (EmailFetchingCriterionChoices.ALL, EmailFetchingCriterionChoices.ALL),
        (EmailFetchingCriterionChoices.UNSEEN, EmailFetchingCriterionChoices.UNSEEN),
        (EmailFetchingCriterionChoices.RECENT, EmailFetchingCriterionChoices.RECENT),
        (EmailFetchingCriterionChoices.NEW, EmailFetchingCriterionChoices.NEW),
        (EmailFetchingCriterionChoices.OLD, EmailFetchingCriterionChoices.OLD),
        (EmailFetchingCriterionChoices.FLAGGED, EmailFetchingCriterionChoices.FLAGGED),
        (EmailFetchingCriterionChoices.DRAFT, EmailFetchingCriterionChoices.DRAFT),
        (
            EmailFetchingCriterionChoices.ANSWERED,
            EmailFetchingCriterionChoices.ANSWERED,
        ),
    ],
)
def test_IMAPFetcher_makeFetchingCriterion_otherCriterion(
    faker, criterionName, expectedResult
):
    fake_datetime = faker.date_time_this_decade(tzinfo=faker.pytimezone())

    with freeze_time(fake_datetime):
        result = IMAPFetcher.makeFetchingCriterion(criterionName)

    assert result == expectedResult


@pytest.mark.django_db
def test_IMAPFetcher___init___success(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")

    result = IMAPFetcher(imap_mailboxModel.account)

    assert result.account == imap_mailboxModel.account
    assert result._mailClient == mock_IMAP4.return_value
    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailboxModel.account.mail_address, imap_mailboxModel.account.password
    )
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___connectionError(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___badProtocol(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    imap_mailboxModel.account.protocol = EmailProtocolChoices.POP3

    with pytest.raises(ValueError, match="not supported"):
        IMAPFetcher(imap_mailboxModel.account)

    spy_IMAPFetcher_connectToHost.assert_not_called()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___loginError(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.return_value.login.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailboxModel.account.mail_address, imap_mailboxModel.account.password
    )
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___init___loginBadResponse(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    spy_IMAPFetcher_connectToHost = mocker.spy(IMAPFetcher, "connectToHost")
    mock_IMAP4.return_value.login.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imap_mailboxModel.account)

    spy_IMAPFetcher_connectToHost.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailboxModel.account.mail_address, imap_mailboxModel.account.password
    )
    mock_logger.error.assert_called()


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
def test_IMAPFetcher_connectToHost_success(
    imap_mailboxModel, mock_logger, mock_IMAP4, mail_host_port, timeout
):
    imap_mailboxModel.account.mail_host_port = mail_host_port
    imap_mailboxModel.account.timeout = timeout

    IMAPFetcher(imap_mailboxModel.account)

    kwargs = {"host": imap_mailboxModel.account.mail_host}
    if mail_host_port:
        kwargs["port"] = mail_host_port
    if timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_connectToHost_exception(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account)

    kwargs = {"host": imap_mailboxModel.account.mail_host}
    if port := imap_mailboxModel.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imap_mailboxModel.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_success(imap_mailboxModel, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imap_mailboxModel.account).test()

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_badResponse(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.noop.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imap_mailboxModel.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_account_exception(imap_mailboxModel, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.noop.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_success(imap_mailboxModel, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imap_mailboxModel.account).test(imap_mailboxModel)

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_wrongMailbox(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        IMAPFetcher(imap_mailboxModel.account).test(wrongMailbox)

    mock_IMAP4.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAPFetcher_test_mailbox_badResponse(
    imap_mailboxModel, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
        IMAPFetcher(imap_mailboxModel.account).test(imap_mailboxModel)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailboxModel.name), readonly=True
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
    imap_mailboxModel, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).side_effect = AssertionError

    with pytest.raises(MailboxError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account).test(imap_mailboxModel)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailboxModel.name), readonly=True
        )
    assert mock_IMAP4.return_value.check.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.check.assert_called_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_badResponse_ignored(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    IMAPFetcher(imap_mailboxModel.account).test(imap_mailboxModel)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_test_mailbox_exception_ignored(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    IMAPFetcher(imap_mailboxModel.account).test(imap_mailboxModel)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_success(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]

    result = IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
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
def test_IMAPFetcher_fetchEmails_wrongMailbox(imap_mailboxModel, mock_logger):
    wrongMailbox = baker.make(MailboxModel)

    with pytest.raises(ValueError, match="is not in"):
        IMAPFetcher(imap_mailboxModel.account).fetchEmails(wrongMailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_badCriterion(imap_mailboxModel, mock_logger):
    with pytest.raises(ValueError, match="not available via"):
        IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raisingFunction, expectedCalls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAPFetcher_fetchEmails_badResponse(
    imap_mailboxModel, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
        IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel)

    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailboxModel.name), readonly=True
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
    imap_mailboxModel, mock_logger, mock_IMAP4, raisingFunction, expectedCalls
):
    getattr(mock_IMAP4.return_value, raisingFunction).side_effect = AssertionError

    with pytest.raises(MailboxError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel)

    assert mock_IMAP4.return_value.select.call_count == expectedCalls[0]
    if expectedCalls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailboxModel.name), readonly=True
        )

    assert mock_IMAP4.return_value.uid.call_count == expectedCalls[1]
    if expectedCalls[1]:
        mock_IMAP4.return_value.uid.assert_called_with("SEARCH", "ALL")
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchEmails_badResponse_ignored(
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    result = IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
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
    mocker, imap_mailboxModel, mock_logger, mock_IMAP4
):
    expectedUidFetchCalls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    result = IMAPFetcher(imap_mailboxModel.account).fetchEmails(imap_mailboxModel)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expectedUidFetchCalls
    )
    mock_IMAP4.return_value.select.assert_called_with(
        utf7_encode(imap_mailboxModel.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expectedUidFetchCalls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expectedUidFetchCalls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_success(imap_mailboxModel, mock_logger, mock_IMAP4):
    result = IMAPFetcher(imap_mailboxModel.account).fetchMailboxes()

    assert result == mock_IMAP4.return_value.list.return_value[1]
    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_badResponse(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.list.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAPFetcher(imap_mailboxModel.account).fetchMailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_fetchMailboxes_exception(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.list.side_effect = AssertionError

    with pytest.raises(MailAccountError, match="AssertionError occured"):
        IMAPFetcher(imap_mailboxModel.account).fetchMailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_success(imap_mailboxModel, mock_logger, mock_IMAP4):
    IMAPFetcher(imap_mailboxModel.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_noClient(imap_mailboxModel, mock_logger, mock_IMAP4):
    fetcher = IMAPFetcher(imap_mailboxModel.account)
    fetcher._mailClient = None

    fetcher.close()

    mock_IMAP4.return_value.logout.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_badResponse(imap_mailboxModel, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.return_value = ("NO", [b""])

    IMAPFetcher(imap_mailboxModel.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher_close_exception(imap_mailboxModel, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.side_effect = AssertionError

    IMAPFetcher(imap_mailboxModel.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAPFetcher___str__(imap_mailboxModel):
    result = str(IMAPFetcher(imap_mailboxModel.account))

    assert str(imap_mailboxModel.account) in result
    assert IMAPFetcher.__name__ in result


@pytest.mark.django_db
def test_IMAPFetcher_context_manager(imap_mailboxModel, mock_logger, mock_IMAP4):
    with IMAPFetcher(imap_mailboxModel.account):
        pass

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAPFetcher_context_manager_exception(
    imap_mailboxModel, mock_logger, mock_IMAP4
):
    with pytest.raises(AssertionError), IMAPFetcher(imap_mailboxModel.account):
        raise AssertionError

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_called()
