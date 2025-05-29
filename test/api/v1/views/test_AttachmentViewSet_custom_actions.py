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

"""Test module for :mod:`api.v1.views.AttachmentViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response

from api.v1.views import AttachmentViewSet
from core.models import Attachment


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
    mocker.patch("api.v1.views.AttachmentViewSet.open", mock_open)
    return mock_open


@pytest.fixture
def mock_os_path_exists(mocker):
    return mocker.patch(
        "api.v1.views.AttachmentViewSet.os.path.exists",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_Attachment_queryset_as_file(mocker, fake_file):
    return mocker.patch(
        "api.v1.views.AttachmentViewSet.Attachment.queryset_as_file",
        return_value=fake_file,
    )


@pytest.mark.django_db
def test_download_noauth(
    fake_attachment,
    noauth_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    fake_attachment,
    other_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    mock_open.side_effect = FileNotFoundError
    mock_os_path_exists.return_value = False

    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(fake_attachment.file_path)


@pytest.mark.django_db
def test_download_auth_owner(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(fake_attachment.file_path)
    mock_open.assert_called_once_with(fake_attachment.file_path, "rb")
    assert "Content-Disposition" in response.headers
    assert f'filename="{fake_attachment.file_name}"' in response["Content-Disposition"]
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
def test_batch_download_noauth(noauth_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": [1]},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_auth_other(other_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": [1, 2]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(response, Response)


@pytest.mark.django_db
def test_batch_download_no_ids_auth_owner(
    owner_api_client, custom_list_action_url, mock_Attachment_queryset_as_file
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert isinstance(response, Response)
    mock_Attachment_queryset_as_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("ids", [[1], [1, 5], [1, 2, 100]])
def test_batch_download_auth_owner(
    fake_file_bytes,
    owner_user,
    owner_api_client,
    custom_list_action_url,
    mock_Attachment_queryset_as_file,
    ids,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": ids},
    )
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert 'filename="attachments.zip"' in response["Content-Disposition"]
    assert b"".join(response.streaming_content) == fake_file_bytes
    mock_Attachment_queryset_as_file.assert_called_once()
    assert list(mock_Attachment_queryset_as_file.call_args.args[0]) == list(
        Attachment.objects.filter(pk__in=ids, email__mailbox__account__user=owner_user)
    )


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_attachment, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_attachment, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated other user client.
    """
    response = other_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_attachment, owner_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated owner user client.
    """
    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is True
