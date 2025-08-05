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

"""Test module for :mod:`api.v1.views.MailboxViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response

from api.v1.views import MailboxViewSet
from core.constants import EmailFetchingCriterionChoices
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from test.conftest import fake_mailbox


@pytest.fixture
def mock_Mailbox_test_connection(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Mailbox.test_connection", autospec=True
    )


@pytest.fixture
def mock_Mailbox_fetch(mocker):
    return mocker.patch("api.v1.views.MailboxViewSet.Mailbox.fetch", autospec=True)


@pytest.fixture
def mock_Mailbox_add_emails_from_file(mocker):
    captured_streams = []

    def capture_stream(*args, **kwargs):
        captured_streams.extend(arg.read() for arg in args if hasattr(arg, "read"))
        captured_streams.extend(
            kwarg.read() for kwarg in kwargs.values() if hasattr(kwarg, "read")
        )

    mock_Mailbox_add_emails_from_file = mocker.patch(
        "api.v1.views.MailboxViewSet.Mailbox.add_emails_from_file",
        autospec=True,
        side_effect=capture_stream,
    )

    mock_Mailbox_add_emails_from_file.captured_streams = captured_streams
    return mock_Mailbox_add_emails_from_file


@pytest.fixture
def mock_Email_queryset_as_file(mocker, fake_file):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Email.queryset_as_file",
        return_value=fake_file,
    )


@pytest.mark.django_db
def test_test_mailbox_noauth(
    fake_mailbox,
    noauth_api_client,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with an unauthenticated user client."""
    previous_is_healthy = fake_mailbox.is_healthy

    response = noauth_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_test_connection.assert_not_called()
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is previous_is_healthy
    assert "name" not in response.data


@pytest.mark.django_db
def test_test_mailbox_auth_other(
    fake_mailbox,
    other_api_client,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated other user client."""
    previous_is_healthy = fake_mailbox.is_healthy

    response = other_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_test_connection.assert_not_called()
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is previous_is_healthy
    assert "name" not in response.data


@pytest.mark.django_db
def test_test_mailbox_success_auth_owner(
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert response.data["result"] is True
    assert "error" not in response.data
    mock_Mailbox_test_connection.assert_called_once_with(fake_mailbox)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_connection_side_effect", [MailboxError, MailAccountError]
)
def test_test_mailbox_failure_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
    test_connection_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_test_connection.side_effect = test_connection_side_effect(
        fake_error_message
    )

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert response.data["result"] is False
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Mailbox_test_connection.assert_called_once_with(fake_mailbox)


@pytest.mark.django_db
def test_fetching_options_noauth(
    noauth_api_client,
    custom_detail_action_url,
    fake_mailbox,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetching_options` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCHING_OPTIONS, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "options" not in response.data


@pytest.mark.django_db
def test_fetching_options_auth_other(
    other_api_client,
    custom_detail_action_url,
    fake_mailbox,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetching_options` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCHING_OPTIONS, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "options" not in response.data


@pytest.mark.django_db
def test_fetching_options_auth_owner(
    owner_api_client,
    custom_detail_action_url,
    fake_mailbox,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetching_options` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCHING_OPTIONS, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["options"] == fake_mailbox.get_available_fetching_criteria()


@pytest.mark.django_db
def test_fetch_all_noauth(
    fake_mailbox,
    noauth_api_client,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with an unauthenticated user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = noauth_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_fetch.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_fetch_all_auth_other(
    fake_mailbox,
    other_api_client,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated other user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = other_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_fetch.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_fetch_all_success_auth_owner(
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert "error" not in response.data
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
@pytest.mark.parametrize("fetch_side_effect", [MailboxError, MailAccountError])
def test_fetch_all_failure_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    mock_Mailbox_fetch,
    custom_detail_action_url,
    fetch_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_fetch.side_effect = fetch_side_effect(fake_error_message)

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
def test_download_noauth(
    faker,
    fake_mailbox,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_DOWNLOAD, fake_mailbox
        ),
        {"file_format": faker.word()},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_other(
    faker,
    fake_mailbox,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_DOWNLOAD, fake_mailbox
        ),
        {"file_format": faker.word()},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_no_format_auth_owner(
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.download` action
    with the authenticated owner user client.
    """

    response = owner_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_DOWNLOAD, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_no_emails_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.download` action
    with the authenticated owner user client.
    """
    fake_mailbox.emails.all().delete()

    response = owner_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_DOWNLOAD, fake_mailbox
        ),
        {"file_format": faker.word()},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_owner(
    faker,
    fake_file_bytes,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Email_queryset_as_file,
):
    """Tests the get method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.download` action
    with the authenticated owner user client.
    """
    fake_format = faker.word()

    response = owner_api_client.get(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_DOWNLOAD, fake_mailbox
        ),
        {"file_format": fake_format},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{fake_mailbox.name}.{fake_format.split("[")[0]}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == fake_file_bytes
    mock_Email_queryset_as_file.assert_called_once()
    assert list(mock_Email_queryset_as_file.call_args.args[0]) == list(
        fake_mailbox.emails.all()
    )
    assert mock_Email_queryset_as_file.call_args.args[1] == fake_format


@pytest.mark.django_db
def test_upload_mailbox_noauth(
    faker,
    fake_mailbox,
    noauth_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with an unauthenticated user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = noauth_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_add_emails_from_file.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_upload_mailbox_auth_other(
    faker,
    fake_mailbox,
    other_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated other user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = other_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_add_emails_from_file.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_upload_mailbox_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    mock_Mailbox_add_emails_from_file.assert_called_once()
    assert mock_Mailbox_add_emails_from_file.call_args.args[0] == fake_mailbox
    assert len(mock_Mailbox_add_emails_from_file.captured_streams) == 1
    assert mock_Mailbox_add_emails_from_file.captured_streams[0] == fake_file.getvalue()
    assert mock_Mailbox_add_emails_from_file.call_args.args[2] == fake_format


@pytest.mark.django_db
def test_upload_mailbox_no_file_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"format": fake_format},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_Mailbox_add_emails_from_file.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_upload_mailbox_no_format_auth_owner(
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    assert fake_mailbox.emails.all().count() == 1

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_Mailbox_add_emails_from_file.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_upload_mailbox_bad_file_or_format_auth_owner(
    faker,
    fake_mailbox,
    owner_api_client,
    custom_detail_action_url,
    mock_Mailbox_add_emails_from_file,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    mock_Mailbox_add_emails_from_file.side_effect = ValueError(faker.text())
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == str(mock_Mailbox_add_emails_from_file.side_effect)
    mock_Mailbox_add_emails_from_file.assert_called_once()
    assert fake_mailbox.emails.all().count() == 1
    assert "name" not in response.data


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_mailbox, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_mailbox, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_mailbox, owner_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is True
