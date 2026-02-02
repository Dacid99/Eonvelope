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

"""Test module for the :class:`IMAP4Fetcher` class."""

import datetime
import re
from imaplib import Time2Internaldate

import pytest
from freezegun import freeze_time
from imap_tools.imap_utf7 import utf7_encode
from model_bakery import baker

from core.constants import (
    EmailFetchingCriterionChoices,
    EmailProtocolChoices,
    MailboxTypeChoices,
)
from core.models import Mailbox
from core.utils.fetchers import IMAP4Fetcher
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from core.utils.mail_parsing import parse_IMAP_mailbox_data


class FakeIMAP4Error(Exception):
    """Helper exception to patch the IMAP4error member of IMAP4."""


@pytest.fixture
def imap_mailbox(fake_mailbox):
    """Extends :func:`test.conftest.fake_mailbox` to have IMAP4 as protocol."""
    fake_mailbox.account.protocol = EmailProtocolChoices.IMAP4
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_IMAP4(mocker, faker):
    """Mocks an :class:`imaplib.IMAP4` with all positive method responses."""
    mock_IMAP4 = mocker.patch(
        "core.utils.fetchers.IMAP4Fetcher.imaplib.IMAP4", autospec=True
    )
    mock_IMAP4.error = FakeIMAP4Error
    fake_response = faker.sentence().encode("utf-8")
    mock_IMAP4.return_value.capabilities = []
    mock_IMAP4.return_value.login.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.authenticate.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.noop.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.check.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.list.return_value = (
        "OK",
        [
            utf7_encode(f'(\\{type_choice}) "/" {word}')
            for word, type_choice in zip(
                faker.words(),
                faker.random_elements(MailboxTypeChoices.values),
                strict=False,
            )
        ],
    )
    mock_IMAP4.return_value.select.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.unselect.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.append.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.uid.side_effect = lambda cmd, *args: (
        (
            "OK",
            [(b"(", fake_response, b")"), (b"(", fake_response, b")")],
        )
        if cmd == "FETCH"
        else ("OK", [fake_response, b""])
    )
    mock_IMAP4.return_value.logout.return_value = ("BYE", [fake_response])
    return mock_IMAP4


@pytest.mark.parametrize(
    "criterion_name, expected_time_delta",
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_IMAP4Fetcher_make_fetching_criterion_date_criterion(
    faker, criterion_name, expected_time_delta
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.make_fetching_query`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)
    expected_criterion = f"SENTSINCE {
        Time2Internaldate(fake_datetime - expected_time_delta).split(' ')[0].strip('" ')
    }"

    with freeze_time(fake_datetime):
        result = IMAP4Fetcher.make_fetching_criterion(criterion_name, "value")

    assert result == expected_criterion


def test_IMAP4Fetcher_make_fetching_criterion_sentsince():
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.make_fetching_query`
    in different cases of date criteria.
    """
    result = IMAP4Fetcher.make_fetching_criterion(
        EmailFetchingCriterionChoices.SENTSINCE, "2009-01-12"
    )

    assert result == "SENTSINCE 12-Jan-2009"


@pytest.mark.parametrize(
    "criterion_name, expected_result",
    [
        (EmailFetchingCriterionChoices.ALL, "ALL"),
        (EmailFetchingCriterionChoices.UNSEEN, "UNSEEN"),
        (EmailFetchingCriterionChoices.SEEN, "SEEN"),
        (EmailFetchingCriterionChoices.RECENT, "RECENT"),
        (EmailFetchingCriterionChoices.NEW, "NEW"),
        (EmailFetchingCriterionChoices.OLD, "OLD"),
        (EmailFetchingCriterionChoices.FLAGGED, "FLAGGED"),
        (EmailFetchingCriterionChoices.UNFLAGGED, "UNFLAGGED"),
        (EmailFetchingCriterionChoices.DRAFT, "DRAFT"),
        (EmailFetchingCriterionChoices.UNDRAFT, "UNDRAFT"),
        (EmailFetchingCriterionChoices.DELETED, "DELETED"),
        (EmailFetchingCriterionChoices.UNDELETED, "UNDELETED"),
        (EmailFetchingCriterionChoices.ANSWERED, "ANSWERED"),
        (EmailFetchingCriterionChoices.UNANSWERED, "UNANSWERED"),
    ],
)
def test_IMAP4Fetcher_make_fetching_criterion_criterion__no_arg(
    criterion_name, expected_result
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.make_fetching_query`
    in different cases of non-date criteria.
    """
    result = IMAP4Fetcher.make_fetching_criterion(criterion_name, "value")

    assert result == expected_result


@pytest.mark.parametrize(
    "criterion_name, expected_result_template",
    [
        (EmailFetchingCriterionChoices.SUBJECT, "SUBJECT {}"),
        (EmailFetchingCriterionChoices.KEYWORD, "KEYWORD {}"),
        (EmailFetchingCriterionChoices.UNKEYWORD, "UNKEYWORD {}"),
        (EmailFetchingCriterionChoices.LARGER, "LARGER {}"),
        (EmailFetchingCriterionChoices.SMALLER, "SMALLER {}"),
        (EmailFetchingCriterionChoices.BODY, "BODY {}"),
        (EmailFetchingCriterionChoices.FROM, "FROM {}"),
    ],
)
def test_IMAP4Fetcher_make_fetching_criterion_criterion_with_arg(
    faker, criterion_name, expected_result_template
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.make_fetching_query`
    in different cases of non-date criteria.
    """
    fake_criterion_arg = faker.word()
    result = IMAP4Fetcher.make_fetching_criterion(criterion_name, fake_criterion_arg)

    assert result == expected_result_template.format(fake_criterion_arg)


@pytest.mark.django_db
def test_IMAP4Fetcher___init___success(mocker, imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of success.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")

    result = IMAP4Fetcher(imap_mailbox.account)

    assert result.account == imap_mailbox.account
    assert result._mail_client == mock_IMAP4.return_value
    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___connection_error(
    mocker, fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of failure establishing a connection.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    mock_IMAP4.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init____bad_protocol(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of the mailbox has a non-IMAP protocol.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    imap_mailbox.account.protocol = EmailProtocolChoices.POP3

    with pytest.raises(ValueError, match=re.compile("protocol", re.IGNORECASE)):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_not_called()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___login_error(
    mocker, fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of an error logging in.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    mock_IMAP4.return_value.login.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___login__bad_response(
    mocker, fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of a bad response logging in.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    mock_IMAP4.return_value.login.return_value = ("NO", [fake_error_message.encode()])

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init__success__utf_8_credentials(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__init__`
    in case of success with non-ASCII credentials.
    """
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    mock_IMAP4.return_value.login.side_effect = UnicodeEncodeError(
        "ascii", "pwd", 0, 1, "utf-8"
    )

    IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_IMAP4.return_value.authenticate.assert_called_once()
    assert mock_IMAP4.return_value.authenticate.call_args[0][0] == "PLAIN"
    assert mock_IMAP4.return_value.authenticate.call_args[0][1](
        "request"
    ) == b"\0" + imap_mailbox.account.mail_address.encode(
        "utf-8"
    ) + b"\0" + imap_mailbox.account.password.encode(
        "utf-8"
    )

    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mail_host_port",
    [
        123,
        None,
    ],
)
def test_IMAP4Fetcher_connect_to_host__success(
    imap_mailbox, mock_logger, mock_IMAP4, mail_host_port
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.connect_to_host`
    in case of success.
    """
    imap_mailbox.account.mail_host_port = mail_host_port

    IMAP4Fetcher(imap_mailbox.account)

    kwargs = {
        "host": imap_mailbox.account.mail_host,
        "timeout": imap_mailbox.account.timeout,
    }
    if mail_host_port:
        kwargs["port"] = mail_host_port
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_connect_to_host__exception(
    fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.connect_to_host`
    in case of an error.
    """
    mock_IMAP4.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account)

    kwargs = {"host": imap_mailbox.account.mail_host}
    if port := imap_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := imap_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_account__success(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    result = IMAP4Fetcher(imap_mailbox.account).test()

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_account__bad_response(
    fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of a bad response with no mailbox given.
    """
    mock_IMAP4.return_value.noop.return_value = ("NO", [fake_error_message.encode()])

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_account__exception(
    fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of an error with no mailbox given.
    """
    mock_IMAP4.return_value.noop.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_mailbox__success(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with a mailbox given.
    """
    result = IMAP4Fetcher(imap_mailbox.account).test(imap_mailbox)

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_mailbox__wrong_mailbox(
    fake_other_account, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success the given mailbox doesn't belong to the given account.
    """
    wrong_mailbox = baker.make(Mailbox, account=fake_other_account)

    with pytest.raises(ValueError, match="is not in"):
        IMAP4Fetcher(imap_mailbox.account).test(wrong_mailbox)

    mock_IMAP4.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAP4Fetcher_test_mailbox__bad_response(
    fake_error_message,
    imap_mailbox,
    mock_logger,
    mock_IMAP4,
    raising_function,
    expected_calls,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of a bad response with a given mailbox.
    """
    getattr(mock_IMAP4.return_value, raising_function).return_value = (
        "NO",
        [fake_error_message.encode()],
    )

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).test(imap_mailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailbox.name), readonly=True
        )
    assert mock_IMAP4.return_value.check.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_IMAP4.return_value.check.assert_called_with()
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAP4Fetcher_test_mailbox__exception(
    fake_error_message,
    imap_mailbox,
    mock_logger,
    mock_IMAP4,
    raising_function,
    expected_calls,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of an error with a given mailbox.
    """
    getattr(mock_IMAP4.return_value, raising_function).side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).test(imap_mailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    assert mock_IMAP4.return_value.select.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailbox.name), readonly=True
        )
    assert mock_IMAP4.return_value.check.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_IMAP4.return_value.check.assert_called_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_mailbox__bad_response__ignored(
    imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of a ignored bad response with a given mailbox.
    """
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    IMAP4Fetcher(imap_mailbox.account).test(imap_mailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_mailbox__exception__ignored(
    imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of an ignored error with a given mailbox.
    """
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    IMAP4Fetcher(imap_mailbox.account).test(imap_mailbox)

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    mock_IMAP4.return_value.check.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__success__sort__single_batch(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of success using the SORT action.
    """
    mock_IMAP4.return_value.capabilities = ["SORT"]
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            b",".join(mock_IMAP4.return_value.uid.side_effect("SORT")[1][0].split()),
            "(RFC822)",
        )
    ]

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ]
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SORT", "(DATE)", "UTF-8", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__success__sort__multi_batch(
    mocker, monkeypatch, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of success using the SORT action.
    """
    mock_IMAP4.return_value.capabilities = ["SORT"]
    monkeypatch.setattr(IMAP4Fetcher, "EMAIL_FETCH_BATCH_SIZE", 1)
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            item,
            "(RFC822)",
        )
        for item in mock_IMAP4.return_value.uid.side_effect("SORT")[1][0].split()
    ]

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ] * len(expected_uid_fetch_calls)
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SORT", "(DATE)", "UTF-8", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__success__search__single_batch(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of success using the SEARCH action.
    """
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            b",".join(mock_IMAP4.return_value.uid.side_effect("SEARCH")[1][0].split()),
            "(RFC822)",
        )
    ]

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ]
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__success__search__multi_batch(
    mocker, monkeypatch, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of success using the SEARCH action.
    """
    monkeypatch.setattr(IMAP4Fetcher, "EMAIL_FETCH_BATCH_SIZE", 1)
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            item,
            "(RFC822)",
        )
        for item in mock_IMAP4.return_value.uid.side_effect("SEARCH")[1][0].split()
    ]

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ] * len(expected_uid_fetch_calls)
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__wrong_mailbox(
    fake_other_account, imap_mailbox, mock_logger
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case the given mailbox does not belong to the given account.
    """
    wrong_mailbox = baker.make(Mailbox, account=fake_other_account)

    with pytest.raises(ValueError, match=re.compile("mailbox", re.IGNORECASE)):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(wrong_mailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__bad_criterion(imap_mailbox, mock_logger):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an unavailable criterion.
    """
    with pytest.raises(ValueError, match=re.compile("criterion", re.IGNORECASE)):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAP4Fetcher_fetch_emails__bad_response(
    fake_error_message,
    imap_mailbox,
    mock_logger,
    mock_IMAP4,
    raising_function,
    expected_calls,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of a bad response.
    """
    getattr(mock_IMAP4.return_value, raising_function).return_value = (
        "NO",
        [fake_error_message.encode()],
    )
    getattr(mock_IMAP4.return_value, raising_function).side_effect = None

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert mock_IMAP4.return_value.select.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailbox.name), readonly=True
        )

    assert mock_IMAP4.return_value.uid.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_IMAP4.return_value.uid.assert_called_with("SEARCH", "ALL")
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAP4Fetcher_fetch_emails__exception(
    fake_error_message,
    imap_mailbox,
    mock_logger,
    mock_IMAP4,
    raising_function,
    expected_calls,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an error.
    """
    getattr(mock_IMAP4.return_value, raising_function).side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert mock_IMAP4.return_value.select.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_IMAP4.return_value.select.assert_called_with(
            utf7_encode(imap_mailbox.name), readonly=True
        )

    assert mock_IMAP4.return_value.uid.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_IMAP4.return_value.uid.assert_called_with("SEARCH", "ALL")
    mock_IMAP4.return_value.unselect.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__bad_response__ignored(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an ignored bad response.
    """
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            b",".join(mock_IMAP4.return_value.uid.side_effect("SEARCH")[1][0].split()),
            "(RFC822)",
        )
    ]
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ]
    mock_IMAP4.return_value.select.assert_called_once_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails__exception__ignored(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an ignored error.
    """
    expected_uid_fetch_calls = [
        mocker.call(
            "FETCH",
            b",".join(mock_IMAP4.return_value.uid.side_effect("SEARCH")[1][0].split()),
            "(RFC822)",
        )
    ]
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [
        content[1] for content in mock_IMAP4.return_value.uid.side_effect("FETCH")[1]
    ]
    mock_IMAP4.return_value.select.assert_called_with(
        utf7_encode(imap_mailbox.name), readonly=True
    )
    assert mock_IMAP4.return_value.uid.call_count == len(expected_uid_fetch_calls) + 1
    mock_IMAP4.return_value.uid.assert_has_calls(
        [mocker.call("SEARCH", "ALL"), *expected_uid_fetch_calls]
    )
    mock_IMAP4.return_value.unselect.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_mailboxes__success(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
    in case of success.
    """
    result = IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    assert len(mock_IMAP4.return_value.list.return_value) == len(result)
    assert all(
        item == parse_IMAP_mailbox_data(return_value)
        for item, return_value in zip(
            result, mock_IMAP4.return_value.list.return_value[1], strict=True
        )
    )
    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_mailboxes__bad_response(
    fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
    in case of a bad response.
    """
    mock_IMAP4.return_value.list.return_value = ("NO", [fake_error_message.encode()])

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_mailboxes__exception(
    fake_error_message, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
    in case of an error.
    """
    mock_IMAP4.return_value.list.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_restore__success(
    imap_mailbox, fake_email_with_file, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    IMAP4Fetcher(imap_mailbox.account).restore(fake_email_with_file)

    with fake_email_with_file.open_file() as email_file:
        mock_IMAP4.return_value.append.assert_called_once_with(
            fake_email_with_file.mailbox.name, None, None, email_file.read()
        )
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_restore__no_file(
    imap_mailbox, fake_email, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case the email has no file.
    """
    with pytest.raises(FileNotFoundError):
        IMAP4Fetcher(imap_mailbox.account).restore(fake_email)

    mock_IMAP4.return_value.append.assert_not_called()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_restore__wrong_mailbox(
    imap_mailbox,
    fake_email_with_file,
    fake_other_mailbox,
    mock_logger,
    mock_IMAP4,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case the email does not belong to a mailbox of the fetchers account.
    """
    fake_email_with_file.mailbox = fake_other_mailbox
    fake_email_with_file.save()

    with pytest.raises(ValueError, match=re.compile("mailbox", re.IGNORECASE)):
        IMAP4Fetcher(imap_mailbox.account).restore(fake_email_with_file)

    mock_IMAP4.return_value.append.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_restore__bad_response(
    fake_error_message, imap_mailbox, fake_email_with_file, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of a bad response.
    """
    mock_IMAP4.return_value.append.return_value = ("NO", [fake_error_message.encode()])

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).restore(fake_email_with_file)

    mock_IMAP4.return_value.append.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_restore__exception(
    fake_error_message, fake_email_with_file, imap_mailbox, mock_logger, mock_IMAP4
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of an error.
    """
    mock_IMAP4.return_value.append.side_effect = AssertionError(fake_error_message)

    with pytest.raises(MailboxError, match=fake_error_message):
        IMAP4Fetcher(imap_mailbox.account).restore(fake_email_with_file)

    mock_IMAP4.return_value.append.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close__success(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.close`
    in case of success.
    """
    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close__bad_response(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.close`
    in case of a bad response.
    """
    mock_IMAP4.return_value.logout.return_value = ("NO", [b""])

    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close__exception(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.close`
    in case of an error.
    """
    mock_IMAP4.return_value.logout.side_effect = AssertionError

    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___str__(imap_mailbox):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.__str__`."""
    result = str(IMAP4Fetcher(imap_mailbox.account))

    assert str(imap_mailbox.account) in result
    assert IMAP4Fetcher.__name__ in result


@pytest.mark.django_db
def test_IMAP4Fetcher_context_manager(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests the context managing of :class:`core.utils.fetchers.IMAP4Fetcher`."""
    with IMAP4Fetcher(imap_mailbox.account):
        pass

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_context_manager_exception(imap_mailbox, mock_logger, mock_IMAP4):
    """Tests the context managing of :class:`core.utils.fetchers.IMAP4Fetcher`
    in case of an error.
    """
    with pytest.raises(AssertionError), IMAP4Fetcher(imap_mailbox.account):
        raise AssertionError

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_called()
