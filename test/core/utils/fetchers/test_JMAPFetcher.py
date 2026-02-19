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

import re
from collections.abc import Iterable, Sized

import jmapc
import pytest
import requests
import urllib3.exceptions

from core.constants import (
    EmailProtocolChoices,
    MailboxTypeChoices,
)
from core.utils import FetchingCriterion
from core.utils.fetchers import JMAPFetcher
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


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
def mock_JMAP_request_handler(faker, fake_get_response_data, fake_query_response_data):
    """Handler for fake JMAP responses."""

    def handle_request(methods):
        if isinstance(methods, Iterable):
            return [
                jmapc.methods.InvocationResponse(
                    id=faker.word(), response=handle_request(method)
                )
                for method in methods
            ]

        if isinstance(methods, jmapc.methods.IdentityGet):
            return jmapc.methods.IdentityGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.MailboxGet):
            fake_get_response_data.update(
                data=[
                    jmapc.Mailbox(
                        name=word,
                        role=role.lower(),
                    )
                    for word, role in zip(
                        faker.words(),
                        faker.random_elements(MailboxTypeChoices.values),
                        strict=False,
                    )
                ]
            )
            return jmapc.methods.MailboxGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.EmailGet):
            fake_get_response_data.update(
                data=[jmapc.Email(blob_id=word) for word in faker.words()]
            )
            return jmapc.methods.EmailGetResponse(**fake_get_response_data)
        if isinstance(methods, jmapc.methods.MailboxQuery):
            return jmapc.methods.MailboxQueryResponse(**fake_query_response_data)
        if isinstance(methods, jmapc.methods.EmailQuery):
            return jmapc.methods.EmailQueryResponse(**fake_query_response_data)
        if isinstance(methods, jmapc.methods.CustomMethod):
            return jmapc.methods.CustomResponse(
                account_id=faker.word(), data=fake_query_response_data
            )
        raise TypeError("This request is not implemented in the mock_handler.")

    return handle_request


@pytest.fixture
def mock_JMAP_error_response_handler(faker):
    """Handler for fake JMAP error responses."""

    def error_response_handler(request):
        return (
            [
                jmapc.methods.InvocationResponseOrError(
                    id=faker.word(), response=jmapc.Error(type=faker.word())
                )
            ]
            * len(request)
            if isinstance(request, Sized)
            else jmapc.Error(type=faker.word())
        )

    return error_response_handler


@pytest.fixture
def mock_JMAP__bad_response_handler(faker, fake_get_response_data):
    """Handler for fake bad JMAP responses."""

    def bad_response_handler(request):
        return (
            [
                jmapc.methods.InvocationResponse(
                    id=faker.word(),
                    response=jmapc.methods.ThreadGetResponse(**fake_get_response_data),
                )
            ]
            * len(request)
            if isinstance(request, Sized)
            else jmapc.methods.ThreadGetResponse(**fake_get_response_data)
        )

    return bad_response_handler


@pytest.fixture(autouse=True)
def mock_JMAP_client(mocker, faker, mock_JMAP_request_handler):
    """Mocks the :class:`jmapc.Client` class."""
    mock_JMAP_client = mocker.patch(
        "core.utils.fetchers.JMAPFetcher.jmapc.Client", autospec=True
    )
    mock_JMAP_client.create_with_api_token.return_value = mock_JMAP_client.return_value
    mock_JMAP_client.create_with_password.return_value = mock_JMAP_client.return_value
    mock_JMAP_client.return_value.upload_blob.return_value = jmapc.Blob(
        id=faker.word(), type=faker.word(), size=faker.random.randint(0, 100)
    )
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_request_handler
    type(mock_JMAP_client.return_value).requests_session = mocker.PropertyMock(
        return_value=mocker.Mock(spec=requests.Session)
    )
    type(mock_JMAP_client.return_value).jmap_session = mocker.PropertyMock(
        return_value=mocker.Mock()
    )

    return mock_JMAP_client


@pytest.mark.parametrize("mail_host_port", [123, None])
@pytest.mark.parametrize("mail_address", ["test@mail.org", None])
@pytest.mark.parametrize("config_allow_insecure", [True, False])
@pytest.mark.parametrize("account_allow_insecure", [True, False])
def test_JMAPFetcher___init___success(
    override_config,
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    account_allow_insecure,
    config_allow_insecure,
    mail_address,
    mail_host_port,
):
    """Test the constructor of JMAPFetcher in case of success."""
    jmap_mailbox.account.mail_address = mail_address
    jmap_mailbox.account.mail_host_port = mail_host_port
    jmap_mailbox.account.allow_insecure_connection = account_allow_insecure

    with override_config(ALLOW_INSECURE_CONNECTIONS=config_allow_insecure):
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
    assert mock_JMAP_client.return_value.requests_session.return_value.verify is not (
        config_allow_insecure and account_allow_insecure
    )
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.parametrize(
    "error",
    [requests.HTTPError, requests.ConnectionError, urllib3.exceptions.HTTPError],
)
def test_JMAPFetcher___init____failure(
    fake_error_message,
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    error,
):
    """Test the constructor of JMAPFetcher in case of an request error."""
    mock_JMAP_client.create_with_password.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account)

    mock_JMAP_client.create_with_password.assert_called_once()
    mock_logger.exception.assert_called()


def test_JMAPFetcher_test_account__success(jmap_mailbox, mock_logger, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    result = JMAPFetcher(jmap_mailbox.account).test()

    assert result is None
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_account_non_single_response(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = jmapc.ClientError(
        fake_error_message, result=None
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).test()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_account__error_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP_error_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_error_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).test()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_account__bad_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP__bad_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP__bad_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).test()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_test_account__requests_error(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client, error
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).test()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_mailbox__success(jmap_mailbox, mock_logger, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with mailbox given.
    """
    result = JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    assert result is None
    mock_JMAP_client.return_value.request.assert_called()
    assert mock_JMAP_client.return_value.request.call_count == 2
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_test_mailbox__failure(
    fake_error_message,
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    error,
):
    """Test the constructor of JMAPFetcher in case of an request error."""
    mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_mailbox_non_single_response(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = jmapc.ClientError(
        fake_error_message, result=None
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_mailbox__wrong_mailbox(
    fake_other_mailbox,
    jmap_mailbox,
    mock_JMAP_client,
):
    """Test the constructor of JMAPFetcher in case of an request error."""
    with pytest.raises(ValueError, match=re.compile("mailbox", re.IGNORECASE)):
        JMAPFetcher(jmap_mailbox.account).test(fake_other_mailbox)

    mock_JMAP_client.return_value.request.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_mailbox__error_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP_error_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_error_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_test_mailbox__bad_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP__bad_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP__bad_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).test(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_mailboxes__success(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
    in case of success.
    """
    result = JMAPFetcher(jmap_mailbox.account).fetch_mailboxes()

    assert result
    assert len(result[0]) == 2
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_fetch_mailboxes__failure(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client, error
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_mailboxes`
    in case of success.
    """
    mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).fetch_mailboxes()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_mailboxes_non_single_response(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = jmapc.ClientError(
        fake_error_message, result=None
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).fetch_mailboxes()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_mailboxes__error_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP_error_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_error_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).fetch_mailboxes()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_mailboxes__bad_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP__bad_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP__bad_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).fetch_mailboxes()

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails__success(jmap_mailbox, mock_logger, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of success.
    """
    result = JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    assert result
    mock_JMAP_client.return_value.request.assert_called()
    mock_JMAP_client.return_value.requests_session.get.assert_called()
    assert mock_JMAP_client.return_value.request.call_count == 2
    mock_logger.debug.assert_called()
    mock_logger.info.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_fetch_emails__failure_request(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client, error
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an error with request.
    """
    mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_JMAP_client.return_value.requests_session.get.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_fetch_emails__failure_download(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client, error
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.fetch_emails`
    in case of an error with request.
    """
    mock_JMAP_client.return_value.requests_session.get.side_effect = error(
        fake_error_message
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called()
    assert mock_JMAP_client.return_value.request.call_count == 2
    mock_JMAP_client.return_value.requests_session.get.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails_non_single_response(
    fake_error_message, mock_logger, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = jmapc.ClientError(
        fake_error_message, result=None
    )

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails__error_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP_error_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_error_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_JMAP_client.return_value.requests_session.get.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails__bad_response(
    jmap_mailbox,
    mock_logger,
    mock_JMAP_client,
    mock_JMAP__bad_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP__bad_response_handler

    with pytest.raises(MailAccountError):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(jmap_mailbox)

    mock_JMAP_client.return_value.request.assert_called_once()
    mock_JMAP_client.return_value.requests_session.get.assert_not_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails__wrong_mailbox(
    fake_other_mailbox,
    jmap_mailbox,
    mock_JMAP_client,
):
    """Test the constructor of JMAPFetcher in case of an request error."""
    with pytest.raises(ValueError, match=re.compile("mailbox", re.IGNORECASE)):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(fake_other_mailbox)

    mock_JMAP_client.return_value.request.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_fetch_emails__bad_criterion(
    jmap_mailbox,
    mock_JMAP_client,
):
    """Test the constructor of JMAPFetcher in case of an request error."""
    with pytest.raises(ValueError, match=re.compile("criterion", re.IGNORECASE)):
        JMAPFetcher(jmap_mailbox.account).fetch_emails(
            jmap_mailbox, FetchingCriterion("NO_CRIT")
        )

    mock_JMAP_client.return_value.request.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_restore__success(
    fake_email_with_file, mock_logger, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_restore__failure_upload_blob(
    fake_error_message,
    mock_logger,
    fake_email_with_file,
    jmap_mailbox,
    mock_JMAP_client,
    error,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    mock_JMAP_client.return_value.upload_blob.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_not_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [requests.HTTPError, requests.ConnectionError])
def test_JMAPFetcher_restore__failure_request(
    fake_error_message,
    mock_logger,
    fake_email_with_file,
    jmap_mailbox,
    mock_JMAP_client,
    error,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    mock_JMAP_client.return_value.request.side_effect = error(fake_error_message)

    with pytest.raises(MailAccountError, match=fake_error_message):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_restore__error_response(
    fake_email_with_file,
    mock_logger,
    jmap_mailbox,
    mock_JMAP_client,
    mock_JMAP_error_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP_error_response_handler

    with pytest.raises(MailboxError):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_restore__bad_response(
    fake_email_with_file,
    mock_logger,
    jmap_mailbox,
    mock_JMAP_client,
    mock_JMAP__bad_response_handler,
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.test`
    in case of success with no mailbox given.
    """
    mock_JMAP_client.return_value.request.side_effect = mock_JMAP__bad_response_handler

    with pytest.raises(MailboxError):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_called_once()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_JMAPFetcher_restore__no_file(
    fake_email_with_file, jmap_mailbox, mock_JMAP_client
):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    mock_JMAP_client.return_value.upload_blob.side_effect = FileNotFoundError

    with pytest.raises(FileNotFoundError):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email_with_file)

    mock_JMAP_client.return_value.upload_blob.assert_called_once()
    mock_JMAP_client.return_value.request.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_restore__no_filepath(fake_email, jmap_mailbox, mock_JMAP_client):
    """Tests :func:`core.utils.fetchers.IMAP4Fetcher.restore`
    in case of success.
    """
    with pytest.raises(FileNotFoundError):
        JMAPFetcher(jmap_mailbox.account).restore(fake_email)

    mock_JMAP_client.return_value.upload_blob.assert_not_called()
    mock_JMAP_client.return_value.request.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_close__success(jmap_mailbox, mock_logger):
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
    mock_logger.exception.assert_not_called()


@pytest.mark.django_db
def test_JMAPFetcher_context_manager_exception(jmap_mailbox, mock_logger):
    """Tests the context managing of :class:`core.utils.fetchers.JMAPFetcher`
    in case of an error.
    """
    with pytest.raises(AssertionError), JMAPFetcher(jmap_mailbox.account):
        raise AssertionError

    mock_logger.error.assert_called()
