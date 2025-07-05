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

"""Test module for the :class:`IMAP4Fetcher` class."""

import datetime
import logging
from imaplib import Time2Internaldate

import pytest
from freezegun import freeze_time
from imap_tools.imap_utf7 import utf7_encode
from model_bakery import baker

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import Mailbox
from core.utils.fetchers import IMAP4Fetcher
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


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
def imap_mailbox(fake_mailbox):
    fake_mailbox.account.protocol = EmailProtocolChoices.IMAP
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_IMAP4(mocker, faker):
    mock_IMAP4 = mocker.patch(
        "core.utils.fetchers.IMAP4Fetcher.imaplib.IMAP4", autospec=True
    )
    mock_IMAP4.error = FakeIMAP4error
    fake_response = faker.sentence().encode("utf-8")
    mock_IMAP4.return_value.login.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.authenticate.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.noop.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.check.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.list.return_value = ("OK", fake_response.split())
    mock_IMAP4.return_value.select.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.unselect.return_value = ("OK", [fake_response])
    mock_IMAP4.return_value.uid.return_value = ("OK", [fake_response, b""])
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
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)
    expected_criterion = f"SENTSINCE {
        Time2Internaldate(fake_datetime - expected_time_delta).split(' ')[0].strip('" ')
    }"

    with freeze_time(fake_datetime):
        result = IMAP4Fetcher.make_fetching_criterion(criterion_name)

    assert result == expected_criterion


@pytest.mark.parametrize(
    "criterion_name, expected_result",
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
def test_IMAP4Fetcher_make_fetching_criterion_other_criterion(
    faker, criterion_name, expected_result
):
    fake_datetime = faker.date_time_this_decade(tzinfo=faker.pytimezone())

    with freeze_time(fake_datetime):
        result = IMAP4Fetcher.make_fetching_criterion(criterion_name)

    assert result == expected_result


@pytest.mark.django_db
def test_IMAP4Fetcher___init___success(mocker, imap_mailbox, mock_logger, mock_IMAP4):
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
    mocker, faker, imap_mailbox, mock_logger, mock_IMAP4
):
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    fake_error_message = faker.sentence()
    mock_IMAP4.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___bad_protocol(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    imap_mailbox.account.protocol = EmailProtocolChoices.POP3

    with pytest.raises(ValueError, match="not supported"):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_not_called()
    mock_IMAP4.return_value.login.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___login_error(
    mocker, faker, imap_mailbox, mock_logger, mock_IMAP4
):
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    fake_error_message = faker.sentence()
    mock_IMAP4.return_value.login.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___login_bad_response(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    spy_IMAP4Fetcher_connect_to_host = mocker.spy(IMAP4Fetcher, "connect_to_host")
    mock_IMAP4.return_value.login.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAP4Fetcher(imap_mailbox.account)

    spy_IMAP4Fetcher_connect_to_host.assert_called_once()
    mock_IMAP4.return_value.login.assert_called_once_with(
        imap_mailbox.account.mail_address, imap_mailbox.account.password
    )
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___init___utf_8_credentials(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
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
    "mail_host_port, timeout",
    [
        (123, 300),
        (123, None),
        (None, 300),
        (None, None),
    ],
)
def test_IMAP4Fetcher_connect_to_host_success(
    imap_mailbox, mock_logger, mock_IMAP4, mail_host_port, timeout
):
    imap_mailbox.account.mail_host_port = mail_host_port
    imap_mailbox.account.timeout = timeout

    IMAP4Fetcher(imap_mailbox.account)

    kwargs = {"host": imap_mailbox.account.mail_host}
    if mail_host_port:
        kwargs["port"] = mail_host_port
    if timeout:
        kwargs["timeout"] = timeout
    mock_IMAP4.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_connect_to_host_exception(
    faker, imap_mailbox, mock_logger, mock_IMAP4
):
    fake_error_message = faker.sentence()
    mock_IMAP4.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
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
def test_IMAP4Fetcher_test_account_success(imap_mailbox, mock_logger, mock_IMAP4):
    result = IMAP4Fetcher(imap_mailbox.account).test()

    assert result is None
    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_account_bad_response(imap_mailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.noop.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAP4Fetcher(imap_mailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_account_exception(
    faker, imap_mailbox, mock_logger, mock_IMAP4
):
    fake_error_message = faker.sentence()
    mock_IMAP4.return_value.noop.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        IMAP4Fetcher(imap_mailbox.account).test()

    mock_IMAP4.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_test_mailbox_success(imap_mailbox, mock_logger, mock_IMAP4):
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
def test_IMAP4Fetcher_test_mailbox_wrong_mailbox(imap_mailbox, mock_logger, mock_IMAP4):
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        IMAP4Fetcher(imap_mailbox.account).test(wrong_mailbox)

    mock_IMAP4.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("check", (1, 1))]
)
def test_IMAP4Fetcher_test_mailbox_bad_response(
    imap_mailbox, mock_logger, mock_IMAP4, raising_function, expected_calls
):
    getattr(mock_IMAP4.return_value, raising_function).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
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
def test_IMAP4Fetcher_test_mailbox_exception(
    faker, imap_mailbox, mock_logger, mock_IMAP4, raising_function, expected_calls
):
    fake_error_message = faker.sentence()
    getattr(mock_IMAP4.return_value, raising_function).side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(MailboxError, match=f"AssertionError.*?{fake_error_message}"):
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
def test_IMAP4Fetcher_test_mailbox_bad_response_ignored(
    imap_mailbox, mock_logger, mock_IMAP4
):
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
def test_IMAP4Fetcher_test_mailbox_exception_ignored(
    imap_mailbox, mock_logger, mock_IMAP4
):
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
def test_IMAP4Fetcher_fetch_emails_success(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    expected_uid_fetch_calls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expected_uid_fetch_calls
    )
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
def test_IMAP4Fetcher_fetch_emails_wrong_mailbox(imap_mailbox, mock_logger):
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(wrong_mailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_emails_bad_criterion(imap_mailbox, mock_logger):
    with pytest.raises(ValueError, match="not available via"):
        IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("select", (1, 0)), ("uid", (1, 1))]
)
def test_IMAP4Fetcher_fetch_emails_bad_response(
    imap_mailbox, mock_logger, mock_IMAP4, raising_function, expected_calls
):
    getattr(mock_IMAP4.return_value, raising_function).return_value = ("NO", [b""])

    with pytest.raises(MailboxError, match="Bad server response"):
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
def test_IMAP4Fetcher_fetch_emails_exception(
    faker, imap_mailbox, mock_logger, mock_IMAP4, raising_function, expected_calls
):
    fake_error_message = faker.sentence()
    getattr(mock_IMAP4.return_value, raising_function).side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(MailboxError, match=f"AssertionError.*?{fake_error_message}"):
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
def test_IMAP4Fetcher_fetch_emails_bad_response_ignored(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    expected_uid_fetch_calls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.return_value = ("NO", [b""])

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expected_uid_fetch_calls
    )
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
def test_IMAP4Fetcher_fetch_emails_exception_ignored(
    mocker, imap_mailbox, mock_logger, mock_IMAP4
):
    expected_uid_fetch_calls = [
        mocker.call("FETCH", uID, "(RFC822)")
        for uID in mock_IMAP4.return_value.uid.return_value[1][0].split()
    ]
    mock_IMAP4.return_value.unselect.side_effect = AssertionError

    result = IMAP4Fetcher(imap_mailbox.account).fetch_emails(imap_mailbox)

    assert result == [mock_IMAP4.return_value.uid.return_value[1][0][1]] * len(
        expected_uid_fetch_calls
    )
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
def test_IMAP4Fetcher_fetch_mailboxes_success(imap_mailbox, mock_logger, mock_IMAP4):
    result = IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    assert result == mock_IMAP4.return_value.list.return_value[1]
    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_mailboxes_bad_response(
    imap_mailbox, mock_logger, mock_IMAP4
):
    mock_IMAP4.return_value.list.return_value = ("NO", [b""])

    with pytest.raises(MailAccountError, match="Bad server response"):
        IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_fetch_mailboxes_exception(
    faker, imap_mailbox, mock_logger, mock_IMAP4
):
    fake_error_message = faker.sentence()
    mock_IMAP4.return_value.list.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        IMAP4Fetcher(imap_mailbox.account).fetch_mailboxes()

    mock_IMAP4.return_value.list.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close_success(imap_mailbox, mock_logger, mock_IMAP4):
    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close_no_client(imap_mailbox, mock_logger, mock_IMAP4):
    fetcher = IMAP4Fetcher(imap_mailbox.account)
    fetcher._mail_client = None

    fetcher.close()

    mock_IMAP4.return_value.logout.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close_bad_response(imap_mailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.return_value = ("NO", [b""])

    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_close_exception(imap_mailbox, mock_logger, mock_IMAP4):
    mock_IMAP4.return_value.logout.side_effect = AssertionError

    IMAP4Fetcher(imap_mailbox.account).close()

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_IMAP4Fetcher___str__(imap_mailbox):
    result = str(IMAP4Fetcher(imap_mailbox.account))

    assert str(imap_mailbox.account) in result
    assert IMAP4Fetcher.__name__ in result


@pytest.mark.django_db
def test_IMAP4Fetcher_context_manager(imap_mailbox, mock_logger, mock_IMAP4):
    with IMAP4Fetcher(imap_mailbox.account):
        pass

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_IMAP4Fetcher_context_manager_exception(imap_mailbox, mock_logger, mock_IMAP4):
    with pytest.raises(AssertionError), IMAP4Fetcher(imap_mailbox.account):
        raise AssertionError

    mock_IMAP4.return_value.logout.assert_called_once()
    mock_logger.error.assert_called()
