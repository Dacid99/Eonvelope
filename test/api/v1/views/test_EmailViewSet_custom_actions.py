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

"""Test module for :mod:`api.v1.views.EmailViewSet`'s custom actions."""

from __future__ import annotations

import os

import pytest
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response

from api.v1.views import EmailViewSet
from core.models import Email


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
    mocker.patch("api.v1.views.EmailViewSet.open", mock_open)
    return mock_open


@pytest.fixture
def mock_os_path_exists(mocker):
    return mocker.patch(
        "api.v1.views.EmailViewSet.os.path.exists",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_Email_queryset_as_file(mocker, fake_file):
    return mocker.patch(
        "api.v1.views.EmailViewSet.Email.queryset_as_file",
        return_value=fake_file,
    )


@pytest.fixture
def mock_Email_sub_conversation(mocker, fake_email):
    return mocker.patch(
        "api.v1.views.EmailViewSet.Email.sub_conversation",
        autospec=True,
        return_value=[fake_email],
    )


@pytest.fixture
def mock_Email_full_conversation(mocker, fake_email):
    return mocker.patch(
        "api.v1.views.EmailViewSet.Email.full_conversation",
        autospec=True,
        return_value=[fake_email],
    )


@pytest.mark.django_db
def test_download_noauth(
    fake_email,
    noauth_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD, fake_email
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    fake_email,
    other_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action with the authenticated owner user client."""
    mock_os_path_exists.return_value = False
    mock_open.side_effect = FileNotFoundError

    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(fake_email.eml_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD, fake_email
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(fake_email.eml_filepath)
    mock_open.assert_called_once_with(fake_email.eml_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(fake_email.eml_filepath)}"'
        in response["Content-Disposition"]
    )
    assert "attachment" in response["Content-Disposition"]
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "message/rfc822"
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
def test_download_html_noauth(
    fake_email,
    noauth_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download_html` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_HTML, fake_email
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_html_auth_other(
    fake_email,
    other_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download_html` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_HTML, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_html_no_file_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download_html` action with the authenticated owner user client."""
    mock_os_path_exists.return_value = False
    mock_open.side_effect = FileNotFoundError

    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_HTML, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(fake_email.html_filepath)


@pytest.mark.django_db
def test_download_html_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download_html` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_HTML, fake_email
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(fake_email.html_filepath)
    mock_open.assert_called_once_with(fake_email.html_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(fake_email.html_filepath)}"'
        in response["Content-Disposition"]
    )
    assert "inline" in response["Content-Disposition"]
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "text/html"
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "Content-Security-Policy" in response.headers
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
def test_batch_download_noauth(faker, noauth_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"id": [1, 2], "file_format": faker.word()},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_auth_other(faker, other_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"file_format": faker.word(), "id": [1, 2]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_no_ids_auth_owner(
    faker, owner_api_client, custom_list_action_url
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"file_format": faker.word()},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_no_format_auth_owner(owner_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"id": [1, 2]},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_bad_format_auth_owner(owner_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"file_format": "unimplemented", "id": [1, 2]},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response, Response)


@pytest.mark.django_db
@pytest.mark.parametrize("ids", [[1], [1, 5], [1, 2, 100]])
def test_batch_download_auth_owner(
    faker,
    fake_file_bytes,
    owner_user,
    owner_api_client,
    custom_list_action_url,
    mock_Email_queryset_as_file,
    ids,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.download` action
    with the authenticated owner user client.
    """
    fake_format = faker.word()

    response = owner_api_client.get(
        custom_list_action_url(EmailViewSet, EmailViewSet.URL_NAME_DOWNLOAD_BATCH),
        {"file_format": fake_format, "id": ids},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="emails.{fake_format.split("[")[0]}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == fake_file_bytes
    mock_Email_queryset_as_file.assert_called_once()
    assert list(mock_Email_queryset_as_file.call_args.args[0]) == list(
        Email.objects.filter(pk__in=ids, mailbox__account__user=owner_user)
    )
    assert mock_Email_queryset_as_file.call_args.args[1] == fake_format


@pytest.mark.django_db
def test_sub_conversation_noauth(
    fake_email,
    noauth_api_client,
    custom_detail_action_url,
    mock_Email_sub_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.sub_conversation` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_SUBCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Email_sub_conversation.assert_not_called()


@pytest.mark.django_db
def test_sub_conversation_auth_other(
    fake_email,
    other_api_client,
    custom_detail_action_url,
    mock_Email_sub_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.sub_conversation` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_SUBCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Email_sub_conversation.assert_not_called()


@pytest.mark.django_db
def test_sub_conversation_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_Email_sub_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.sub_conversation` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_SUBCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == fake_email.id
    mock_Email_sub_conversation.assert_called_once_with(fake_email)


@pytest.mark.django_db
def test_full_conversation_noauth(
    fake_email,
    noauth_api_client,
    custom_detail_action_url,
    mock_Email_full_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.full_conversation` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_FULLCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Email_full_conversation.assert_not_called()


@pytest.mark.django_db
def test_full_conversation_auth_other(
    fake_email,
    other_api_client,
    custom_detail_action_url,
    mock_Email_full_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.full_conversation` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_FULLCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Email_full_conversation.assert_not_called()


@pytest.mark.django_db
def test_full_conversation_auth_owner(
    fake_email,
    owner_api_client,
    custom_detail_action_url,
    mock_Email_full_conversation,
):
    """Tests the get method :func:`api.v1.views.EmailViewSet.EmailViewSet.full_conversation` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_FULLCONVERSATION, fake_email
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == fake_email.id
    mock_Email_full_conversation.assert_called_once_with(fake_email)


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_email, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EmailViewSet.EmailViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_TOGGLE_FAVORITE, fake_email
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_email.refresh_from_db()
    assert fake_email.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_email, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EmailViewSet.EmailViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_TOGGLE_FAVORITE, fake_email
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_email.refresh_from_db()
    assert fake_email.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_email, owner_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EmailViewSet.EmailViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            EmailViewSet, EmailViewSet.URL_NAME_TOGGLE_FAVORITE, fake_email
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_email.refresh_from_db()
    assert fake_email.is_favorite is True
