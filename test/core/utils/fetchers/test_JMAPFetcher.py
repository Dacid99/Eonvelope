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

import jmapc
import pytest
import requests
from freezegun import freeze_time
from jmapc.methods.email import EmailGetResponse
from jmapc.methods.identity import IdentityGet

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.utils.fetchers import JMAPFetcher
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture
def jmap_mailbox(fake_mailbox):
    """Extends :func:`test.conftest.fake_mailbox` to have JMAP as protocol."""
    fake_mailbox.account.protocol = EmailProtocolChoices.JMAP
    fake_mailbox.account.save(update_fields=["protocol"])
    return fake_mailbox


@pytest.fixture
def fake_get_response_data(faker):
    """Fake response data for a /get JMAP request."""
    return {
        "account_id": faker.word(),
        "not_found": [],
        "state": faker.word(),
        "data": faker.json(),
    }


@pytest.fixture
def fake_query_response_data(faker):
    """Fake response data for a /query JMAP request."""
    return {
        "account_id": faker.word(),
        "query_state": faker.word(),
        "can_calculate_changes": faker.pybool(),
        "position": faker.random.randint(0, 10),
        "ids": faker.words(),
        "total": None,
        "limit": None,
    }


@pytest.fixture
def mock_JMAP_request_handler(fake_get_response_data, fake_query_response_data):
    """Handler for the fake JMAP responses."""

    def handle_request(methods):
        if isinstance(methods, list):
            return [handle_request(method) for method in methods]

        if isinstance(methods, jmapc.methods.IdentityGet):
            return jmapc.methods.IdentityGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.MailboxGet):
            return jmapc.methods.MailboxGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.EmailGet):
            return jmapc.methods.EmailGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.MailboxQuery):
            return jmapc.methods.MailboxQueryResponse(**fake_query_response_data)
        if isinstance(methods, jmapc.methods.EmailQuery):
            return jmapc.methods.EmailQueryResponse(**fake_query_response_data)
        raise TypeError("This request is not implemented in the mock_handler.")

    return handle_request


@pytest.fixture(autouse=True)
def mock_JMAP_client(mocker, mock_JMAP_request_handler):
    """Mocks the :class:`jmapc.Client` class."""
    mock_JMAP_client = mocker.patch(
        "core.utils.fetchers.JMAPFetcher.jmapc.Client", autospec=True
    )
    mock_JMAP_client.create_with_api_token.return_value = mock_JMAP_client.return_value
    mock_JMAP_client.create_with_password.return_value = mock_JMAP_client.return_value
    mock_JMAP_client.return_value.upload_blob.return_value = None
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_request_handler

    return mock_JMAP_client


@pytest.mark.parametrize(
    "criterion_name, expected_time_delta",
    [
        (EmailFetchingCriterionChoices.DAILY, datetime.timedelta(days=1)),
        (EmailFetchingCriterionChoices.WEEKLY, datetime.timedelta(weeks=1)),
        (EmailFetchingCriterionChoices.MONTHLY, datetime.timedelta(weeks=4)),
        (EmailFetchingCriterionChoices.ANNUALLY, datetime.timedelta(weeks=52)),
    ],
)
def test_JMAPFetcher_make_fetching_filter_date_criterion(
    faker, criterion_name, expected_time_delta
):
    """Tests :func:`core.utils.fetchers.JMAPFetcher.make_fetching_query`
    in different cases of date criteria.
    """
    fake_datetime = faker.date_time_this_decade(tzinfo=datetime.UTC)
    expected_filter = jmapc.EmailQueryFilterCondition(
        after=fake_datetime - expected_time_delta
    )

    with freeze_time(fake_datetime):
        result = JMAPFetcher.make_fetching_filter(criterion_name, "value")

    assert result == expected_filter


def test_IMAP4Fetcher_make_fetching_filter_sentsince():
    """Tests :func:`core.utils.fetchers.JMAPFetcher.make_fetching_query`
    in case of the sentsince criterion.
    """
    result = JMAPFetcher.make_fetching_filter(
        EmailFetchingCriterionChoices.SENTSINCE, "2013-05-29"
    )

    assert result == jmapc.EmailQueryFilterCondition(
        after=datetime.datetime(2013, 5, 29, tzinfo=datetime.UTC)
    )


@pytest.mark.parametrize(
    "criterion_name, expected_filter_kwarg",
    [
        (EmailFetchingCriterionChoices.ALL, {}),
        (EmailFetchingCriterionChoices.SEEN, {"has_keyword": "$seen"}),
        (EmailFetchingCriterionChoices.DRAFT, {"has_keyword": "$draft"}),
        (EmailFetchingCriterionChoices.ANSWERED, {"has_keyword": "$answered"}),
        (EmailFetchingCriterionChoices.UNSEEN, {"not_keyword": "$seen"}),
        (EmailFetchingCriterionChoices.UNDRAFT, {"not_keyword": "$draft"}),
        (EmailFetchingCriterionChoices.UNANSWERED, {"not_keyword": "$answered"}),
    ],
)
def test_JMAPFetcher_make_fetching_filter_no_arg(criterion_name, expected_filter_kwarg):
    """Tests :func:`core.utils.fetchers.JMAPFetcher.make_fetching_query`
    in different cases of criteria without argument.
    """
    result = JMAPFetcher.make_fetching_filter(criterion_name, "")

    assert result == jmapc.EmailQueryFilterCondition(**expected_filter_kwarg)


@pytest.mark.parametrize(
    "criterion_name, criterion_arg, expected_filter_kwarg",
    [
        (EmailFetchingCriterionChoices.LARGER, 140, {"min_size": 140}),
        (EmailFetchingCriterionChoices.SMALLER, 598, {"max_size": 598}),
        (EmailFetchingCriterionChoices.BODY, "testtext", {"body": "testtext"}),
        (
            EmailFetchingCriterionChoices.FROM,
            "sender@server.com",
            {"mail_from": "sender@server.com"},
        ),
    ],
)
def test_JMAPFetcher_make_fetching_filter_with_arg(
    criterion_name, criterion_arg, expected_filter_kwarg
):
    """Tests :func:`core.utils.fetchers.JMAPFetcher.make_fetching_query`
    in different cases of criteria with argument.
    """
    result = JMAPFetcher.make_fetching_filter(criterion_name, criterion_arg)

    assert result == jmapc.EmailQueryFilterCondition(**expected_filter_kwarg)


@pytest.mark.parametrize("mail_host_port", [123, None])
@pytest.mark.parametrize("mail_address", ["test@mail.org", None])
def test_JMAPFetcher___init___success(
    jmap_mailbox, mock_JMAP_client, mail_address, mail_host_port
):
    """Test the constructor of JMAPFetcher in case of success."""
    jmap_mailbox.account.mail_address = mail_address
    jmap_mailbox.account.mail_host_port = mail_host_port

    fetcher = JMAPFetcher(jmap_mailbox.account)

    assert fetcher._mail_client == mock_JMAP_client.return_value
    if mail_address:
        mock_JMAP_client.create_with_password.assert_called_once_with(
            host=(
                f"{jmap_mailbox.account.mail_host}:{mail_host_port}"
                if mail_host_port
                else jmap_mailbox.account.mail_host
            ),
            user=mail_address,
            password=jmap_mailbox.account.password,
        )
        mock_JMAP_client.create_with_api_token.assert_not_called()
    else:
        mock_JMAP_client.create_with_api_token.assert_called_once_with(
            host=(
                f"{jmap_mailbox.account.mail_host}:{mail_host_port}"
                if mail_host_port
                else jmap_mailbox.account.mail_host
            ),
            api_token=jmap_mailbox.account.password,
        )
        mock_JMAP_client.create_with_password.assert_not_called()


@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher___init___failure(
    fake_error_message,
    jmap_mailbox,
    mock_JMAP_client,
    error,
):
    """Test the constructor of JMAPFetcher in case of failure."""
    mock_JMAP_client.create_with_password.side_effect = error(fake_error_message)

    with pytest.raises(
        MailAccountError, match=f"{error.__name__}.*?{fake_error_message}"
    ):
        JMAPFetcher(jmap_mailbox.account)

    mock_JMAP_client.create_with_password.assert_called_once()


def test_JMAPFetcher_test_account_success(jmap_mailbox, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    result = JMAPFetcher(jmap_mailbox.account).test()

    assert result is None
    mock_JMAP_client.return_value.request.assert_called_once()


# def test_JMAPFetcher_test_account_non_single_response(
#     fake_error_message, jmap_mailbox, mock_JMAP_client
# ):
#     """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
#     in case of success with no mailbox given.
#     """
#     mock_JMAP_client.return_value.request.side_effect = jmapc.ClientError(
#         fake_error_message, result=[]
#     )

#     with pytest.raises(MailAccountError, match=fake_error_message):
#         JMAPFetcher(jmap_mailbox.account).test()

#     mock_JMAP_client.return_value.request.assert_called_once()


# def test_JMAPFetcher_test_account_error_response(
#     fake_error_message, jmap_mailbox, mock_JMAP_client
# ):
#     """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
#     in case of success with no mailbox given.
#     """
#     mock_JMAP_client.return_value.request.side_effect = jmapc.Error(fake_error_message)

#     with pytest.raises(MailAccountError, match=fake_error_message):
#         JMAPFetcher(jmap_mailbox.account).test()

#     mock_JMAP_client.request.assert_called_once()


# def test_JMAPFetcher_test_account_wrong_response(
#     jmap_mailbox,
#     mock_JMAP_client,
#     fake_get_response_data,
# ):
#     """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
#     in case of success with no mailbox given.
#     """
#     mock_JMAP_client.return_value.request.side_effect = jmapc.methods.base.GetResponse(
#         **fake_get_response_data
#     )

#     with pytest.raises(MailAccountError, match=f"BadServerResponseError"):
#         JMAPFetcher(jmap_mailbox.account).test()

#     mock_JMAP_client.request.assert_called_once()


# @pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
# def test_JMAPFetcher_test_account_requests_error(
#     fake_error_message, jmap_mailbox, mock_JMAP_client, error
# ):
#     """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
#     in case of success with no mailbox given.
#     """
#     mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

#     with pytest.raises(
#         MailAccountError, match=f"{error.__name__}.*?{fake_error_message}"
#     ):
#         JMAPFetcher(jmap_mailbox.account).test()

#     mock_JMAP_client.request.assert_called_once()


def test_JMAPFetcher_test_mailbox_success(jmap_mailbox, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with mailbox given.
    """
    result = JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    assert result is None
    mock_JMAP_client.return_value.request.assert_called()
    assert mock_JMAP_client.return_value.request.call_count == 2


# def test_JMAPFetcher_fetch_mailboxes_success(jmap_mailbox, mock_JMAP_client):
#     """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
#     in case of success.
#     """
#     result = JMAPFetcher(jmap_mailbox.account).fake_mailboxes()

#     assert result
#     mock_JMAP_client.return_value.request.assert_called_once()


@pytest.mark.django_db
def test_JMAPFetcher_close_success(jmap_mailbox, mock_logger):
    """Tests :func:`core.utils.fetchers.JMAPFetcher.close`
    in case of success.
    """
    JMAPFetcher(jmap_mailbox.account).close()

    mock_logger.exception.assert_not_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher___str__(jmap_mailbox):
    """Tests :func:`core.utils.fetchers.JMAPFetcher.__str__`."""
    result = str(JMAPFetcher(jmap_mailbox.account))

    assert str(jmap_mailbox.account) in result
    assert JMAPFetcher.__name__ in result


@pytest.mark.django_db
def test_JMAPFetcher_context_manager(jmap_mailbox, mock_logger):
    """Tests the context managing of :class:`core.utils.fetchers.JMAPFetcher`."""
    with JMAPFetcher(jmap_mailbox.account):
        pass

    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_context_manager_exception(jmap_mailbox, mock_logger):
    """Tests the context managing of :class:`core.utils.fetchers.JMAPFetcher`
    in case of an error.
    """
    with pytest.raises(AssertionError), JMAPFetcher(jmap_mailbox.account):
        raise AssertionError

    mock_logger.error.assert_called()
