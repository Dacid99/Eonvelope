# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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
from core.models import Mailbox
from core.utils.fetchers import POP3Fetcher
from core.utils.fetchers.exceptions import MailAccountError


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
def pop3_mailbox(fake_mailbox):
    fake_mailbox.account.protocol = EmailProtocolChoices.POP3
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture(autouse=True)
def mock_POP3(mocker, faker):
    mock_POP3 = mocker.patch(
        "core.utils.fetchers.POP3Fetcher.poplib.POP3", autospec=True
    )
    fake_response = faker.sentence().encode("utf-8")
    mock_POP3.return_value.user.return_value = b"+OK" + fake_response
    mock_POP3.return_value.pass_.return_value = b"+OK" + fake_response
    mock_POP3.return_value.noop.return_value = b"+OK"
    mock_POP3.return_value.list.return_value = b"+OK" + fake_response
    mock_POP3.return_value.list.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3.return_value.retr.return_value = (b"+OK", fake_response.split(), 123)
    mock_POP3.return_value.quit.return_value = b"+OK" + fake_response
    return mock_POP3


@pytest.mark.django_db
def test_POP3Fetcher___init___success(mocker, pop3_mailbox, mock_logger, mock_POP3):
    spy_POP3Fetcher_connect_to_host = mocker.spy(POP3Fetcher, "connect_to_host")

    result = POP3Fetcher(pop3_mailbox.account)

    assert result.account == pop3_mailbox.account
    assert result._mail_client == mock_POP3.return_value
    spy_POP3Fetcher_connect_to_host.assert_called_once()
    mock_POP3.return_value.user.assert_called_once_with(
        pop3_mailbox.account.mail_address
    )
    mock_POP3.return_value.pass_.assert_called_once_with(pop3_mailbox.account.password)
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher___init___connection_error(
    mocker, faker, pop3_mailbox, mock_logger, mock_POP3
):
    spy_POP3Fetcher_connect_to_host = mocker.spy(POP3Fetcher, "connect_to_host")
    fake_error_message = faker.sentence()
    mock_POP3.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account)

    spy_POP3Fetcher_connect_to_host.assert_called_once()
    mock_POP3.return_value.user.assert_not_called()
    mock_POP3.return_value.pass_.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher___init___bad_protocol(
    mocker, pop3_mailbox, mock_logger, mock_POP3
):
    spy_POP3Fetcher_connect_to_host = mocker.spy(POP3Fetcher, "connect_to_host")
    pop3_mailbox.account.protocol = EmailProtocolChoices.IMAP

    with pytest.raises(ValueError, match="protocol"):
        POP3Fetcher(pop3_mailbox.account)

    spy_POP3Fetcher_connect_to_host.assert_not_called()
    mock_POP3.return_value.user.assert_not_called()
    mock_POP3.return_value.pass_.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("user", (1, 0)), ("pass_", (1, 1))]
)
def test_POP3Fetcher___init___exception(
    mocker,
    faker,
    pop3_mailbox,
    mock_logger,
    mock_POP3,
    raising_function,
    expected_calls,
):
    spy_POP3Fetcher_connect_to_host = mocker.spy(POP3Fetcher, "connect_to_host")
    fake_error_message = faker.sentence()
    getattr(mock_POP3.return_value, raising_function).side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account)

    spy_POP3Fetcher_connect_to_host.assert_called_once()
    assert mock_POP3.return_value.user.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_POP3.return_value.user.assert_called_with(
            pop3_mailbox.account.mail_address
        )
    assert mock_POP3.return_value.pass_.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_POP3.return_value.pass_.assert_called_with(pop3_mailbox.account.password)
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "raising_function, expected_calls", [("user", (1, 0)), ("pass_", (1, 1))]
)
def test_POP3Fetcher___init___bad_response(
    mocker, pop3_mailbox, mock_logger, mock_POP3, raising_function, expected_calls
):
    spy_POP3Fetcher_connect_to_host = mocker.spy(POP3Fetcher, "connect_to_host")
    getattr(mock_POP3.return_value, raising_function).return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3_mailbox.account)

    spy_POP3Fetcher_connect_to_host.assert_called_once()
    assert mock_POP3.return_value.user.call_count == expected_calls[0]
    if expected_calls[0]:
        mock_POP3.return_value.user.assert_called_with(
            pop3_mailbox.account.mail_address
        )
    assert mock_POP3.return_value.pass_.call_count == expected_calls[1]
    if expected_calls[1]:
        mock_POP3.return_value.pass_.assert_called_with(pop3_mailbox.account.password)
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
def test_POP3Fetcher_connect_to_host_success(
    pop3_mailbox, mock_logger, mock_POP3, mail_host_port, timeout
):
    pop3_mailbox.account.mail_host_port = mail_host_port
    pop3_mailbox.account.timeout = timeout

    POP3Fetcher(pop3_mailbox.account)

    kwargs = {"host": pop3_mailbox.account.mail_host}
    if mail_host_port:
        kwargs["port"] = mail_host_port
    if timeout:
        kwargs["timeout"] = timeout
    mock_POP3.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_connect_to_host_exception(
    faker, pop3_mailbox, mock_logger, mock_POP3
):
    fake_error_message = faker.sentence()
    mock_POP3.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account)

    kwargs = {"host": pop3_mailbox.account.mail_host}
    if port := pop3_mailbox.account.mail_host_port:
        kwargs["port"] = port
    if timeout := pop3_mailbox.account.timeout:
        kwargs["timeout"] = timeout
    mock_POP3.assert_called_with(**kwargs)
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_success(pop3_mailbox, mock_logger, mock_POP3):
    result = POP3Fetcher(pop3_mailbox.account).test()

    assert result is None
    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_bad_response(pop3_mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.noop.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3_mailbox.account).test()

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_account_exception(
    faker, pop3_mailbox, mock_logger, mock_POP3
):
    fake_error_message = faker.sentence()
    mock_POP3.return_value.noop.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account).test()

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_success(pop3_mailbox, mock_logger, mock_POP3):
    result = POP3Fetcher(pop3_mailbox.account).test(pop3_mailbox)

    assert result is None
    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.list.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_wrong_mailbox(pop3_mailbox, mock_logger, mock_POP3):
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        POP3Fetcher(pop3_mailbox.account).test(wrong_mailbox)

    mock_POP3.return_value.noop.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_bad_response(pop3_mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.list.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3_mailbox.account).test(pop3_mailbox)

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.list.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_test_mailbox_exception(
    faker, pop3_mailbox, mock_logger, mock_POP3
):
    fake_error_message = faker.sentence()
    mock_POP3.return_value.list.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account).test(pop3_mailbox)

    mock_POP3.return_value.noop.assert_called_once_with()
    mock_POP3.return_value.list.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_success(mocker, pop3_mailbox, mock_logger, mock_POP3):
    expected_retr_calls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]

    result = POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox)

    assert result == [b"\n".join(mock_POP3.return_value.retr.return_value[1])] * len(
        expected_retr_calls
    )
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expected_retr_calls)
    mock_POP3.return_value.retr.assert_has_calls(expected_retr_calls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_wrong_mailbox(pop3_mailbox, mock_logger):
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        POP3Fetcher(pop3_mailbox.account).fetch_emails(wrong_mailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_bad_criterion(pop3_mailbox, mock_logger):
    with pytest.raises(ValueError, match="not available via"):
        POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox, "NONE")

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_bad_response(pop3_mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.list.return_value = b"+NO"

    with pytest.raises(MailAccountError, match="Bad server response"):
        POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox)

    mock_POP3.return_value.list.assert_called_once_with()
    mock_POP3.return_value.retr.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_exception(
    faker, pop3_mailbox, mock_logger, mock_POP3
):
    fake_error_message = faker.sentence()
    mock_POP3.return_value.list.side_effect = AssertionError(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"AssertionError.*?{fake_error_message}"
    ):
        POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox)

    mock_POP3.return_value.list.assert_called_once_with()
    mock_POP3.return_value.retr.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_bad_response_ignored(
    mocker, pop3_mailbox, mock_logger, mock_POP3
):
    expected_retr_calls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]
    mock_POP3.return_value.retr.return_value = b"+NO"

    result = POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox)

    assert result == []
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expected_retr_calls)
    mock_POP3.return_value.retr.assert_has_calls(expected_retr_calls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_emails_exception_ignored(
    mocker, pop3_mailbox, mock_logger, mock_POP3
):
    expected_retr_calls = [
        mocker.call(number + 1)
        for number in range(len(mock_POP3.return_value.list.return_value[1]))
    ]
    mock_POP3.return_value.retr.side_effect = AssertionError

    result = POP3Fetcher(pop3_mailbox.account).fetch_emails(pop3_mailbox)

    assert result == []
    mock_POP3.return_value.list.assert_called_once_with()
    assert mock_POP3.return_value.retr.call_count == len(expected_retr_calls)
    mock_POP3.return_value.retr.assert_has_calls(expected_retr_calls)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_fetch_mailboxes(pop3_mailbox):
    result = POP3Fetcher(pop3_mailbox.account).fetch_mailboxes()

    assert result == ["INBOX"]


@pytest.mark.django_db
def test_POP3Fetcher_close_success(pop3_mailbox, mock_logger, mock_POP3):
    POP3Fetcher(pop3_mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_close_bad_response(pop3_mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.quit.return_value = b"+NO"

    POP3Fetcher(pop3_mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher_close_exception(pop3_mailbox, mock_logger, mock_POP3):
    mock_POP3.return_value.quit.side_effect = AssertionError

    POP3Fetcher(pop3_mailbox.account).close()

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_POP3Fetcher___str__(pop3_mailbox):
    result = str(POP3Fetcher(pop3_mailbox.account))

    assert str(pop3_mailbox.account) in result
    assert POP3Fetcher.__name__ in result


@pytest.mark.django_db
def test_POP3Fetcher_context_manager(pop3_mailbox, mock_logger, mock_POP3):
    with POP3Fetcher(pop3_mailbox.account):
        pass
    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_POP3Fetcher_context_manager_exception(pop3_mailbox, mock_logger, mock_POP3):
    with pytest.raises(AssertionError), POP3Fetcher(pop3_mailbox.account):
        raise AssertionError

    mock_POP3.return_value.quit.assert_called_once()
    mock_logger.error.assert_called()
