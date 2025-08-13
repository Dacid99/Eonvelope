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
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework import status
from rest_framework.response import Response

from api.v1.views import AttachmentViewSet
from core.models import Attachment


@pytest.fixture
def mock_Attachment_queryset_as_file(mocker, fake_file):
    return mocker.patch(
        "api.v1.views.AttachmentViewSet.Attachment.queryset_as_file",
        return_value=fake_file,
    )


@pytest.mark.django_db
def test_download_noauth(
    fake_attachment_with_file,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_DOWNLOAD,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_other(
    fake_attachment_with_file,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_DOWNLOAD,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_auth_owner(
    fake_attachment_with_file,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_DOWNLOAD,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{fake_attachment_with_file.file_name}"'
        in response["Content-Disposition"]
    )
    assert "attachment" in response["Content-Disposition"]
    assert (
        b"".join(response.streaming_content)
        == default_storage.open(fake_attachment_with_file.file_path).read()
    )


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
    assert not isinstance(response, FileResponse)


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
    assert not isinstance(response, FileResponse)


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
    assert not isinstance(response, FileResponse)
    mock_Attachment_queryset_as_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "bad_ids",
    [
        ["abc"],
        ["1e2"],
        ["5.3"],
        ["4ur"],
    ],
)
def test_batch_download_bad_ids_auth_owner(
    owner_api_client, custom_list_action_url, mock_Attachment_queryset_as_file, bad_ids
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": bad_ids},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert not isinstance(response, FileResponse)
    mock_Attachment_queryset_as_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "ids, expected_ids",
    [
        (["1"], [1]),
        (["1", " 2", "100"], [1, 2, 100]),
        (["1,2", "10"], [1, 2, 10]),
        (["4,6, 8"], [4, 6, 8]),
    ],
)
def test_batch_download_auth_owner(
    fake_file_bytes,
    owner_user,
    owner_api_client,
    custom_list_action_url,
    mock_Attachment_queryset_as_file,
    ids,
    expected_ids,
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
        Attachment.objects.filter(
            pk__in=expected_ids, email__mailbox__account__user=owner_user
        )
    )


@pytest.mark.django_db
def test_download_thumbnail_noauth(
    fake_attachment_with_file,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_THUMBNAIL,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_thumbnail_auth_other(
    fake_attachment_with_file,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_THUMBNAIL,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_thumbnail_no_file_auth_owner(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_THUMBNAIL, fake_attachment
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_thumbnail_auth_owner(
    fake_attachment_with_file,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_THUMBNAIL,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, FileResponse)
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{fake_attachment_with_file.file_name}"'
        in response["Content-Disposition"]
    )
    assert "inline" in response["Content-Disposition"]
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == fake_attachment_with_file.content_type
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "Content-Security-Policy" in response.headers
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"
    assert (
        b"".join(response.streaming_content)
        == default_storage.open(fake_attachment_with_file.file_path).read()
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
