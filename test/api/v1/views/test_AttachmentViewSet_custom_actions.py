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

"""Test module for :mod:`api.v1.views.AttachmentViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from django.core.files.storage import default_storage
from django.http import FileResponse
from rest_framework import status

from api.v1.views import AttachmentViewSet
from core.models import Attachment


@pytest.fixture
def mock_Attachment_queryset_as_file(mocker, fake_file):
    """Patches `core.models.Attachment.queryset_as_file`."""
    return mocker.patch(
        "api.v1.views.AttachmentViewSet.Attachment.queryset_as_file",
        return_value=fake_file,
    )


@pytest.fixture
def mock_Attachment_share_to_paperless(mocker, faker):
    """Patches `core.models.Attachment.share_to_paperless`."""
    return mocker.patch(
        "core.models.Attachment.Attachment.share_to_paperless",
        autospec=True,
        return_value=faker.uuid4(),
    )


@pytest.fixture
def mock_Attachment_share_to_immich(mocker, faker):
    """Patches `core.models.Attachment.share_to_immich`."""
    return mocker.patch(
        "core.models.Attachment.Attachment.share_to_immich",
        autospec=True,
        return_value={"id": faker.uuid4()},
    )


@pytest.mark.django_db
def test_download__noauth(
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
def test_download__auth_other(
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
def test_download__no_file__auth_owner(
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
def test_download__auth_owner(
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
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == (
        fake_attachment_with_file.content_type or "application/octet-stream"
    )
    assert (
        b"".join(response.streaming_content)
        == default_storage.open(fake_attachment_with_file.file_path).read()
    )


@pytest.mark.django_db
def test_download__auth_admin(
    fake_attachment_with_file,
    admin_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated admin user client.
    """
    response = admin_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_DOWNLOAD,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_batch_download__noauth(noauth_api_client, custom_list_action_url):
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
def test_batch_download__auth_other(other_api_client, custom_list_action_url):
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
def test_batch_download__no_ids__auth_owner(
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
    assert response.data["id"]
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
def test_batch_download__bad_ids__auth_owner(
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
    assert response.data["id"]
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
def test_batch_download__auth_owner(
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
    assert "Content-Type" in response.headers
    assert response.headers["Content-Type"] == "application/zip"
    assert b"".join(response.streaming_content) == fake_file_bytes
    mock_Attachment_queryset_as_file.assert_called_once()
    assert list(mock_Attachment_queryset_as_file.call_args.args[0]) == list(
        Attachment.objects.filter(
            pk__in=expected_ids, email__mailbox__account__user=owner_user
        )
    )


@pytest.mark.django_db
def test_batch_download__auth_admin(admin_api_client, custom_list_action_url):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated admin user client.
    """
    response = admin_api_client.get(
        custom_list_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD_BATCH
        ),
        {"id": [1, 2]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_download_thumbnail__noauth(
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
def test_download_thumbnail__auth_other(
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
def test_download_thumbnail__no_file__auth_owner(
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
def test_download_thumbnail__auth_owner(
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
    assert response.headers["Content-Type"] == (
        fake_attachment_with_file.content_type or "application/octet-stream"
    )
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"
    assert "Content-Security-Policy" in response.headers
    assert response.headers["Content-Security-Policy"] == "frame-ancestors 'self'"
    assert (
        b"".join(response.streaming_content)
        == default_storage.open(fake_attachment_with_file.file_path).read()
    )


@pytest.mark.django_db
def test_download_thumbnail__auth_admin(
    fake_attachment_with_file,
    admin_api_client,
    custom_detail_action_url,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated admin user client.
    """
    response = admin_api_client.get(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_THUMBNAIL,
            fake_attachment_with_file,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert not isinstance(response, FileResponse)


@pytest.mark.django_db
def test_toggle_favorite__noauth(
    faker, fake_attachment, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with an unauthenticated user client.
    """
    previous_is_favorite = bool(faker.random.getrandbits(1))
    fake_attachment.is_favorite = previous_is_favorite
    fake_attachment.save(update_fields=["is_favorite"])

    response = noauth_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is previous_is_favorite


@pytest.mark.django_db
def test_toggle_favorite__auth_other(
    faker, fake_attachment, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated other user client.
    """
    previous_is_favorite = bool(faker.random.getrandbits(1))
    fake_attachment.is_favorite = previous_is_favorite
    fake_attachment.save(update_fields=["is_favorite"])

    response = other_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is previous_is_favorite


@pytest.mark.django_db
@pytest.mark.parametrize("previous_is_favorite", [True, False])
def test_toggle_favorite__auth_owner(
    fake_attachment, owner_api_client, custom_detail_action_url, previous_is_favorite
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated owner user client.
    """
    fake_attachment.is_favorite = previous_is_favorite
    fake_attachment.save(update_fields=["is_favorite"])

    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is not previous_is_favorite


@pytest.mark.django_db
def test_toggle_favorite__auth_admin(
    faker, fake_attachment, admin_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated admin user client.
    """
    previous_is_favorite = bool(faker.random.getrandbits(1))
    fake_attachment.is_favorite = previous_is_favorite
    fake_attachment.save(update_fields=["is_favorite"])

    response = admin_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()
    assert fake_attachment.is_favorite is previous_is_favorite


@pytest.mark.django_db
def test_share_to_paperless__noauth(
    fake_attachment,
    noauth_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_share_to_paperless__auth_other(
    fake_attachment,
    other_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with the authenticated other user client.
    """
    response = other_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_share_to_paperless__auth_owner__success(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with the authenticated owner user client.
    """
    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.data
    assert response.data["data"] == mock_Attachment_share_to_paperless.return_value
    fake_attachment.refresh_from_db()
    mock_Attachment_share_to_paperless.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "error",
    [
        ConnectionError,
        PermissionError,
        ValueError,
        RuntimeError,
    ],
)
def test_share_to_paperless__auth_owner__failure(
    fake_error_message,
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
    error,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with the authenticated owner user client.
    """
    mock_Attachment_share_to_paperless.side_effect = error(fake_error_message)

    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Attachment_share_to_paperless.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
def test_share_to_paperless__auth_owner__no_file(
    fake_error_message,
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with the authenticated owner user client.
    """
    mock_Attachment_share_to_paperless.side_effect = FileNotFoundError

    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data
    mock_Attachment_share_to_paperless.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
def test_share_to_paperless__auth_admin(
    fake_attachment,
    admin_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_paperless,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_paperless` action
    with the authenticated admin user client.
    """
    response = admin_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_PAPERLESS,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_share_to_immich__noauth(
    fake_attachment,
    noauth_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with an unauthenticated user client.
    """
    response = noauth_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_share_to_immich__auth_other(
    fake_attachment,
    other_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with the authenticated other user client.
    """
    response = other_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_share_to_immich__auth_owner__success(
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with the authenticated owner user client.
    """
    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert "data" in response.data
    assert response.data["data"] == mock_Attachment_share_to_immich.return_value
    fake_attachment.refresh_from_db()
    mock_Attachment_share_to_immich.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "error",
    [
        ConnectionError,
        PermissionError,
        ValueError,
        RuntimeError,
    ],
)
def test_share_to_immich__auth_owner__failure(
    fake_error_message,
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
    error,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with the authenticated owner user client.
    """
    mock_Attachment_share_to_immich.side_effect = error(fake_error_message)

    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "detail" in response.data
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Attachment_share_to_immich.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
def test_share_to_immich__auth_owner__no_file(
    fake_error_message,
    fake_attachment,
    owner_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with the authenticated owner user client.
    """
    mock_Attachment_share_to_immich.side_effect = FileNotFoundError

    response = owner_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.data
    mock_Attachment_share_to_immich.assert_called_once_with(fake_attachment)


@pytest.mark.django_db
def test_share_to_immich__auth_admin(
    fake_attachment,
    admin_api_client,
    custom_detail_action_url,
    mock_Attachment_share_to_immich,
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.share_to_immich` action
    with the authenticated admin user client.
    """
    response = admin_api_client.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_SHARE_TO_IMMICH,
            fake_attachment,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()
