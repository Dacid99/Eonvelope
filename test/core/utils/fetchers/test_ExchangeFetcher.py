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

"""Test module for the :class:`ExchangeFetcher` class."""

import datetime
import os

import exchangelib
import exchangelib.errors
import exchangelib.folders
import exchangelib.folders.known_folders
import exchangelib.queryset
import pytest
from freezegun import freeze_time
from model_bakery import baker

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import Mailbox
from core.utils.fetchers import ExchangeFetcher
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


@pytest.fixture
def exchange_mailbox(fake_mailbox):
    """Extends :func:`test.conftest.fake_mailbox` to have Exchange as protocol."""
    fake_mailbox.account.protocol = EmailProtocolChoices.EXCHANGE
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture
def mock_message(mocker, faker):
    """Mocks an :class:`exchangelib.Message` with random mime_content."""
    mock_message = mocker.MagicMock(spec=exchangelib.Message)
    mock_message.mime_content = faker.text().encode()
    return mock_message


@pytest.fixture
def mock_Message(mocker, mock_message):
    """Mocks the :class:`exchangelib.Message` class."""
    return mocker.patch("exchangelib.Message", autospec=True, return_value=mock_message)


@pytest.fixture
def mock_QuerySet(mocker, mock_message):
    """Mocks an :class:`exchangelib.queryset.QuerySet` with mocked :class:`exchangelib.Message`s."""
    mock_QuerySet = mocker.MagicMock(spec=exchangelib.queryset.QuerySet)
    queryset_content = [mock_message, mock_message]
    mock_QuerySet.__iter__.return_value = queryset_content
    mock_QuerySet.order_by.return_value = mock_QuerySet
    mock_QuerySet.all.return_value.__iter__.return_value = queryset_content
    mock_QuerySet.filter.return_value.__iter__.return_value = queryset_content[:1]
    return mock_QuerySet


@pytest.fixture
def mock_Folder(mocker, mock_QuerySet):
    """Mocks an :class:`exchangelib.Folder` with mocked :class:`exchangelib.queryset.QuerySet` as content."""
    mock_Folder = mocker.MagicMock(spec=exchangelib.Folder)
    mock_Folder.all.return_value = mock_QuerySet
    mock_Folder.folder_class.return_value = "IPF.Note"
    return mock_Folder


@pytest.fixture
def mock_msg_folder_root(mocker, faker, mock_Folder):
    """Mocks an :class:`exchangelib.folders.known_folders.MsgFolderRoot` with mocked :class:`exchangelib.Folder` as content."""
    fake_msg_folder_root_path = faker.file_path()
    mock_msg_folder_root = mocker.MagicMock(
        spec=exchangelib.folders.known_folders.MsgFolderRoot
    )
    type(mock_msg_folder_root).absolute = mocker.PropertyMock(
        return_value=fake_msg_folder_root_path
    )
    mock_msg_folder_root.walk.return_value = [
        mock_Folder,
        mocker.Mock(spec=exchangelib.Folder),
        mocker.Mock(),
        mock_Folder,
    ]
    mock_msg_folder_root.__truediv__.return_value = mock_Folder
    mock_msg_folder_root.__truediv__.return_value.__truediv__.return_value = mock_Folder
    type(mock_Folder).absolute = mocker.PropertyMock(
        return_value=os.path.join(fake_msg_folder_root_path, faker.name())
    )
    return mock_msg_folder_root


@pytest.fixture(autouse=True)
def mock_ExchangeAccount(mocker, mock_msg_folder_root):
    """Mocks an :class:`exchangelib.Account` with mocked :class:`exchangelib.folders.known_folders.MsgFolderRoot` as msg_root."""
    mock_ExchangeAccount = mocker.patch(
        "core.utils.fetchers.ExchangeFetcher.exchangelib.Account", autospec=True
    )
    type(mock_ExchangeAccount.return_value).msg_folder_root = mocker.PropertyMock(
        return_value=mock_msg_folder_root
    )

    return mock_ExchangeAccount


@pytest.mark.parametrize(
    "criterion_name, expected_time_delta",
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_ExchangeFetcher_make_fetching_query_date_criterion(
    faker, mock_QuerySet, criterion_name, expected_time_delta
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.make_fetching_query`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)

    with freeze_time(fake_datetime):
        result = ExchangeFetcher.make_fetching_query(criterion_name, "", mock_QuerySet)

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(
        datetime_received__gte=fake_datetime - expected_time_delta
    )


def test_ExchangeFetcher_make_fetching_query_sentsince_criterion(mock_QuerySet):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.make_fetching_query`
    in different cases of date criteria.
    """

    result = ExchangeFetcher.make_fetching_query(
        EmailFetchingCriterionChoices.SENTSINCE, "2010-6-5", mock_QuerySet
    )

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(
        datetime_received__gte=datetime.datetime(2010, 6, 5, tzinfo=datetime.UTC)
    )


@pytest.mark.parametrize(
    "criterion_name, criterion_arg, expected_kwarg",
    [
        (EmailFetchingCriterionChoices.UNSEEN, "", {"is_read": False}),
        (EmailFetchingCriterionChoices.SEEN, "", {"is_read": True}),
        (EmailFetchingCriterionChoices.DRAFT, "", {"is_draft": True}),
        (EmailFetchingCriterionChoices.UNDRAFT, "", {"is_draft": False}),
        (
            EmailFetchingCriterionChoices.SUBJECT,
            "somestring",
            {"subject__contains": "somestring"},
        ),
        (
            EmailFetchingCriterionChoices.BODY,
            "textPart",
            {"body__contains": "textPart"},
        ),
    ],
)
def test_ExchangeFetcher_make_fetching_query_other_criterion(
    mock_QuerySet, criterion_name, criterion_arg, expected_kwarg
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.make_fetching_query`
    in different cases of flag criteria.
    """
    result = ExchangeFetcher.make_fetching_query(
        criterion_name, criterion_arg, mock_QuerySet
    )

    assert result == mock_QuerySet.filter.return_value
    mock_QuerySet.filter.assert_called_once_with(**expected_kwarg)


def test_ExchangeFetcher_make_fetching_query_all_criterion(mock_QuerySet):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.make_fetching_query`
    in case of the ALL criterion.
    """
    result = ExchangeFetcher.make_fetching_query(
        EmailFetchingCriterionChoices.ALL, "", mock_QuerySet
    )

    assert result == mock_QuerySet


@pytest.mark.django_db
def test_ExchangeFetcher___init___success(
    mocker, exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.__init__`
    in case of success.
    """
    spy_ExchangeFetcher_connect_to_host = mocker.spy(ExchangeFetcher, "connect_to_host")

    result = ExchangeFetcher(exchange_mailbox.account)

    assert result.account == exchange_mailbox.account
    assert result._mail_client == mock_ExchangeAccount.return_value.msg_folder_root
    spy_ExchangeFetcher_connect_to_host.assert_called_once()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher___init___failure(
    mocker, fake_error_message, exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.__init__`
    in case of failure.
    """
    type(mock_ExchangeAccount.return_value).msg_folder_root = mocker.PropertyMock(
        side_effect=exchangelib.errors.EWSError(fake_error_message)
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        ExchangeFetcher(exchange_mailbox.account)

    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher___init___bad_protocol(
    mocker, exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.__init__`
    in case of the mailbox has a non-Exchange protocol.
    """
    spy_ExchangeFetcher_connect_to_host = mocker.spy(ExchangeFetcher, "connect_to_host")
    exchange_mailbox.account.protocol = EmailProtocolChoices.POP3

    with pytest.raises(ValueError, match="protocol"):
        ExchangeFetcher(exchange_mailbox.account)

    spy_ExchangeFetcher_connect_to_host.assert_not_called()
    mock_ExchangeAccount.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("http_protocol", ["http://", "https://"])
@pytest.mark.parametrize(
    "mail_host_port",
    [
        123,
        None,
    ],
)
def test_ExchangeFetcher_connect_to_host_hostURL_success(
    exchange_mailbox,
    mock_logger,
    mock_ExchangeAccount,
    mail_host_port,
    http_protocol,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.connect_to_host`
    in different cases of account `mail_host` in URL form, `timeout` and`mail_host_port` settings.
    """
    exchange_mailbox.account.mail_host = http_protocol + "path.MyDomain.tld"
    exchange_mailbox.account.mail_host_port = mail_host_port

    ExchangeFetcher(exchange_mailbox.account)

    mock_ExchangeAccount.assert_called_once()
    assert (
        mock_ExchangeAccount.call_args.kwargs["primary_smtp_address"]
        == exchange_mailbox.account.mail_address
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"], exchangelib.Configuration
    )
    assert (
        mock_ExchangeAccount.call_args.kwargs["config"].service_endpoint
        == exchange_mailbox.account.mail_host
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"].credentials,
        exchangelib.Credentials,
    )
    assert (
        mock_ExchangeAccount.call_args.kwargs["config"].credentials.username
        == exchange_mailbox.account.mail_address
    )
    assert (
        mock_ExchangeAccount.call_args.kwargs["config"].credentials.password
        == exchange_mailbox.account.password
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"].retry_policy,
        exchangelib.FaultTolerance,
    )
    if exchange_mailbox.account.timeout:
        assert mock_ExchangeAccount.call_args.kwargs[
            "config"
        ].retry_policy.max_wait == (exchange_mailbox.account.timeout)
    assert mock_ExchangeAccount.call_args.kwargs["access_type"] == exchangelib.DELEGATE
    assert mock_ExchangeAccount.call_args.kwargs["autodiscover"] is False
    assert mock_ExchangeAccount.call_args.kwargs[
        "default_timezone"
    ] == exchangelib.EWSTimeZone("UTC")
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mail_host_port",
    [
        123,
        None,
    ],
)
def test_ExchangeFetcher_connect_to_host_hostname_success(
    exchange_mailbox, mock_logger, mock_ExchangeAccount, mail_host_port
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.connect_to_host`
    in cases of success with different combinations of account `mail_host` in hostname form, `timeout` and `mail_host_port` settings.
    """
    exchange_mailbox.account.mail_host = "path.MyDomain.tld"
    exchange_mailbox.account.mail_host_port = mail_host_port
    expected_url = (
        f"{exchange_mailbox.account.mail_host}:{exchange_mailbox.account.mail_host_port}"
        if exchange_mailbox.account.mail_host_port
        else exchange_mailbox.account.mail_host
    )
    ExchangeFetcher(exchange_mailbox.account)

    mock_ExchangeAccount.assert_called_once()
    assert (
        mock_ExchangeAccount.call_args.kwargs["primary_smtp_address"]
        == exchange_mailbox.account.mail_address
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"], exchangelib.Configuration
    )
    assert (
        expected_url in mock_ExchangeAccount.call_args.kwargs["config"].service_endpoint
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"].credentials,
        exchangelib.Credentials,
    )
    assert (
        mock_ExchangeAccount.call_args.kwargs["config"].credentials.username
        == exchange_mailbox.account.mail_address
    )
    assert (
        mock_ExchangeAccount.call_args.kwargs["config"].credentials.password
        == exchange_mailbox.account.password
    )
    assert isinstance(
        mock_ExchangeAccount.call_args.kwargs["config"].retry_policy,
        exchangelib.FaultTolerance,
    )
    if exchange_mailbox.account.timeout:
        assert mock_ExchangeAccount.call_args.kwargs[
            "config"
        ].retry_policy.max_wait == (exchange_mailbox.account.timeout)
    assert mock_ExchangeAccount.call_args.kwargs["access_type"] == exchangelib.DELEGATE
    assert mock_ExchangeAccount.call_args.kwargs["autodiscover"] is False
    assert mock_ExchangeAccount.call_args.kwargs[
        "default_timezone"
    ] == exchangelib.EWSTimeZone("UTC")
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_account_success(
    exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of success with no mailbox given.
    """
    result = ExchangeFetcher(exchange_mailbox.account).test()

    assert result is None
    mock_ExchangeAccount.return_value.msg_folder_root.refresh.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_account_ewserror(
    fake_error_message, exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of an EWSError with no mailbox given.
    """
    mock_ExchangeAccount.return_value.msg_folder_root.refresh.side_effect = (
        exchangelib.errors.EWSError(fake_error_message)
    )

    with pytest.raises(MailAccountError, match=f"EWSError.*?{fake_error_message}"):
        ExchangeFetcher(exchange_mailbox.account).test()

    mock_ExchangeAccount.return_value.msg_folder_root.refresh.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_account_other_exception(
    exchange_mailbox, mock_logger, mock_ExchangeAccount
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of an unexpected error with no mailbox given.
    """
    mock_ExchangeAccount.return_value.msg_folder_root.refresh.side_effect = (
        AssertionError
    )

    with pytest.raises(AssertionError):
        ExchangeFetcher(exchange_mailbox.account).test()

    mock_ExchangeAccount.return_value.msg_folder_root.refresh.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_mailbox_success(
    exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of success with a given mailbox.
    """
    result = ExchangeFetcher(exchange_mailbox.account).test(exchange_mailbox)

    assert result is None
    mock_msg_folder_root.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.return_value.__truediv__.return_value.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.assert_called_once()
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_mailbox_subfolder_success(
    faker, exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of success with a given subfolder mailbox.
    """
    fake_folder_name = exchange_mailbox.name
    fake_subfolder_name = faker.name()
    exchange_mailbox.name = fake_folder_name + "/" + fake_subfolder_name

    result = ExchangeFetcher(exchange_mailbox.account).test(exchange_mailbox)

    assert result is None
    mock_msg_folder_root.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.assert_called_once_with(fake_folder_name)
    mock_msg_folder_root.__truediv__.return_value.__truediv__.return_value.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_called_once_with(
        fake_subfolder_name
    )
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_mailbox_wrong_mailbox(
    exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case the given mailbox does not belong to the given account.
    """
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        ExchangeFetcher(exchange_mailbox.account).test(wrong_mailbox)

    mock_msg_folder_root.refresh.assert_not_called()
    mock_msg_folder_root.__truediv__.return_value.refresh.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_mailbox_ewserror(
    fake_error_message,
    exchange_mailbox,
    mock_logger,
    mock_msg_folder_root,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of an EWSError with a given mailbox.
    """
    mock_msg_folder_root.__truediv__.return_value.refresh.side_effect = (
        exchangelib.errors.EWSError(fake_error_message)
    )

    with pytest.raises(MailboxError, match=f"EWSError.*?{fake_error_message}"):
        ExchangeFetcher(exchange_mailbox.account).test(exchange_mailbox)

    mock_msg_folder_root.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.return_value.refresh.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_test_mailbox_other_exception(
    fake_error_message,
    exchange_mailbox,
    mock_logger,
    mock_msg_folder_root,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.test`
    in case of an unexpected error with a given mailbox.
    """
    mock_msg_folder_root.__truediv__.return_value.refresh.side_effect = AssertionError(
        fake_error_message
    )

    with pytest.raises(AssertionError, match=fake_error_message):
        ExchangeFetcher(exchange_mailbox.account).test(exchange_mailbox)

    mock_msg_folder_root.refresh.assert_called_once_with()
    mock_msg_folder_root.__truediv__.return_value.refresh.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_all_success(
    exchange_mailbox, mock_logger, mock_QuerySet, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case of success.
    """
    result = ExchangeFetcher(exchange_mailbox.account).fetch_emails(exchange_mailbox)

    assert result == [item.mime_content for item in mock_QuerySet.__iter__.return_value]
    mock_QuerySet.order_by.assert_called_once_with("datetime_received")
    mock_msg_folder_root.__truediv__.assert_called_once_with(exchange_mailbox.name)
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_subfolder_all_success(
    faker, exchange_mailbox, mock_logger, mock_QuerySet, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case of success with the given mailbox being a subfolder mailbox.
    """
    fake_folder_name = exchange_mailbox.name
    fake_subfolder_name = faker.name()
    exchange_mailbox.name = fake_folder_name + "/" + fake_subfolder_name

    result = ExchangeFetcher(exchange_mailbox.account).fetch_emails(exchange_mailbox)

    assert result == [item.mime_content for item in mock_QuerySet.__iter__.return_value]
    mock_QuerySet.order_by.assert_called_once_with("datetime_received")
    mock_msg_folder_root.__truediv__.assert_called_once_with(fake_folder_name)
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_called_once_with(
        fake_subfolder_name
    )
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_filter_success(
    exchange_mailbox, mock_logger, mock_QuerySet
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case of success with a criterion other than ALL.
    """
    result = ExchangeFetcher(exchange_mailbox.account).fetch_emails(
        exchange_mailbox, EmailFetchingCriterionChoices.DRAFT
    )

    assert result == [
        item.mime_content
        for item in mock_QuerySet.filter.return_value.__iter__.return_value
    ]
    mock_QuerySet.filter.assert_called_once_with(is_draft=True)
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_wrong_mailbox(exchange_mailbox, mock_logger):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case the given mailbox does not belong to the given account.
    """
    wrong_mailbox = baker.make(Mailbox)

    with pytest.raises(ValueError, match="is not in"):
        ExchangeFetcher(exchange_mailbox.account).fetch_emails(wrong_mailbox)

    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_ewserror_query(
    fake_error_message, exchange_mailbox, mock_logger, mock_Folder
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case of an EWSError.
    """
    mock_Folder.all.side_effect = exchangelib.errors.EWSError(fake_error_message)

    with pytest.raises(MailboxError, match=f"EWSError.*?{fake_error_message}"):
        ExchangeFetcher(exchange_mailbox.account).fetch_emails(exchange_mailbox)

    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_emails_other_exception_query(
    fake_error_message, exchange_mailbox, mock_logger, mock_Folder
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_emails`
    in case of an unexpected error.
    """
    mock_Folder.all.side_effect = AssertionError(fake_error_message)

    with pytest.raises(AssertionError, match=fake_error_message):
        ExchangeFetcher(exchange_mailbox.account).fetch_emails(exchange_mailbox)

    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_mailboxes_success(
    exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_mailboxes`
    in case of success.
    """
    result = ExchangeFetcher(exchange_mailbox.account).fetch_mailboxes()

    mock_msg_folder_root.walk.assert_called()
    assert result == [
        os.path.relpath(
            item.absolute.return_value, mock_msg_folder_root.absolute.return_value
        )
        for item in mock_msg_folder_root.walk.return_value
        if isinstance(item, exchangelib.Folder) and item.folder_class == "IPF.Note"
    ]
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_mailboxes_ewserror_walk(
    fake_error_message, exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_mailboxes`
    in case of an EWSError during walking of the folder structure.
    """
    mock_msg_folder_root.walk.side_effect = exchangelib.errors.EWSError(
        fake_error_message
    )

    with pytest.raises(MailAccountError, match=f"EWSError.*?{fake_error_message}"):
        ExchangeFetcher(exchange_mailbox.account).fetch_mailboxes()

    mock_msg_folder_root.walk.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_fetch_mailboxes_other_exception_walk(
    fake_error_message, exchange_mailbox, mock_logger, mock_msg_folder_root
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.fetch_mailboxes`
    in case of an unexpected error during walking of the folder structure.
    """
    mock_msg_folder_root.walk.side_effect = AssertionError(fake_error_message)

    with pytest.raises(AssertionError, match=fake_error_message):
        ExchangeFetcher(exchange_mailbox.account).fetch_mailboxes()

    mock_msg_folder_root.walk.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_success(
    exchange_mailbox,
    fake_email_with_file,
    mock_logger,
    mock_Message,
    mock_msg_folder_root,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case of success.
    """
    ExchangeFetcher(exchange_mailbox.account).restore(fake_email_with_file)

    with fake_email_with_file.open_file() as email_file:
        mock_Message.assert_called_once_with(
            mime_content=email_file.read(),
            folder=mock_msg_folder_root.__truediv__.return_value,
        )
    mock_Message.return_value.save.assert_called_once_with()
    mock_msg_folder_root.__truediv__.assert_called_once_with(exchange_mailbox.name)
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_not_called()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_success_subfolder(
    faker,
    exchange_mailbox,
    fake_email_with_file,
    mock_logger,
    mock_Message,
    mock_msg_folder_root,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case of success.
    """
    fake_folder_name = exchange_mailbox.name
    fake_subfolder_name = faker.name()
    exchange_mailbox.name = fake_folder_name + "/" + fake_subfolder_name

    ExchangeFetcher(exchange_mailbox.account).restore(fake_email_with_file)

    with fake_email_with_file.open_file() as email_file:
        mock_Message.assert_called_once_with(
            mime_content=email_file.read(),
            folder=mock_msg_folder_root.__truediv__.return_value.__truediv__.return_value,
        )
    mock_Message.return_value.save.assert_called_once_with()
    mock_msg_folder_root.__truediv__.assert_called_once_with(fake_folder_name)
    mock_msg_folder_root.__truediv__.return_value.__truediv__.assert_called_once_with(
        fake_subfolder_name
    )
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_no_file(
    exchange_mailbox, fake_email, mock_logger, mock_Message
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case the email has no file.
    """
    with pytest.raises(FileNotFoundError):
        ExchangeFetcher(exchange_mailbox.account).restore(fake_email)

    mock_Message.assert_not_called()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_wrong_mailbox(
    exchange_mailbox,
    fake_email_with_file,
    fake_other_mailbox,
    mock_logger,
    mock_Message,
    mock_ExchangeAccount,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case the email does not belong to a mailbox of the fetchers account.
    """
    fake_email_with_file.mailbox = fake_other_mailbox
    fake_email_with_file.save()

    with pytest.raises(ValueError):
        ExchangeFetcher(exchange_mailbox.account).restore(fake_email_with_file)

    mock_Message.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_ewserror(
    fake_error_message,
    fake_email_with_file,
    exchange_mailbox,
    mock_logger,
    mock_Message,
    mock_ExchangeAccount,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case of an error.
    """
    mock_Message.return_value.save.side_effect = exchangelib.errors.EWSError(
        fake_error_message
    )

    with pytest.raises(MailboxError, match=f"EWSError.*?{fake_error_message}"):
        ExchangeFetcher(exchange_mailbox.account).restore(fake_email_with_file)

    mock_Message.assert_called_once()
    mock_Message.return_value.save.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_restore_other_error(
    fake_email_with_file,
    exchange_mailbox,
    mock_logger,
    mock_Message,
    mock_ExchangeAccount,
):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.restore`
    in case of an error.
    """
    mock_Message.return_value.save.side_effect = AssertionError

    with pytest.raises(AssertionError):
        ExchangeFetcher(exchange_mailbox.account).restore(fake_email_with_file)

    mock_Message.assert_called_once()
    mock_Message.return_value.save.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_ExchangeFetcher_close_success(exchange_mailbox, mock_logger):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.close`
    in case of success.
    """
    ExchangeFetcher(exchange_mailbox.account).close()

    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher___str__(exchange_mailbox):
    """Tests :func:`core.utils.fetchers.ExchangeFetcher.__str__`."""
    result = str(ExchangeFetcher(exchange_mailbox.account))

    assert str(exchange_mailbox.account) in result
    assert ExchangeFetcher.__name__ in result


@pytest.mark.django_db
def test_ExchangeFetcher_context_manager(exchange_mailbox, mock_logger):
    """Tests the context managing of :class:`core.utils.fetchers.ExchangeFetcher`."""
    with ExchangeFetcher(exchange_mailbox.account):
        pass

    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_ExchangeFetcher_context_manager_exception(exchange_mailbox, mock_logger):
    """Tests the context managing of :class:`core.utils.fetchers.ExchangeFetcher`
    in case of an error.
    """
    with pytest.raises(AssertionError), ExchangeFetcher(exchange_mailbox.account):
        raise AssertionError

    mock_logger.error.assert_called()
