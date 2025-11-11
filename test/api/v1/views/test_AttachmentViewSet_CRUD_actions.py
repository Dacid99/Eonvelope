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

"""Test module for :mod:`api.v1.views.AttachmentViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views import AttachmentViewSet
from core.models import Attachment


@pytest.mark.django_db
def test_list_noauth(fake_attachment, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list_auth_other(fake_attachment, other_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_attachment, owner_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(fake_attachment, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "file_name" not in response.data


@pytest.mark.django_db
def test_get_auth_other(fake_attachment, other_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "file_name" not in response.data


@pytest.mark.django_db
def test_get_auth_owner(fake_attachment, owner_api_client, detail_url):
    """Tests the `list` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["file_name"] == fake_attachment.file_name


@pytest.mark.django_db
def test_patch_noauth(
    fake_attachment, noauth_api_client, attachment_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_patch_auth_other(
    fake_attachment, other_api_client, attachment_payload, detail_url
):
    """Tests the `patch` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.patch(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_patch_auth_owner(
    fake_attachment, owner_api_client, attachment_payload, detail_url
):
    """Tests the `patch` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_put_noauth(fake_attachment, noauth_api_client, attachment_payload, detail_url):
    """Tests the put method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_put_auth_other(
    fake_attachment, other_api_client, attachment_payload, detail_url
):
    """Tests the `put` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.put(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_put_auth_owner(
    fake_attachment, owner_api_client, attachment_payload, detail_url
):
    """Tests the `put` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(
        detail_url(AttachmentViewSet, fake_attachment), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name != attachment_payload["file_name"]


@pytest.mark.django_db
def test_post_noauth(noauth_api_client, attachment_payload, list_url):
    """Tests the post method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(
        list_url(AttachmentViewSet), data=attachment_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "file_name" not in response.data
    with pytest.raises(Attachment.DoesNotExist):
        Attachment.objects.get(file_name=attachment_payload["file_name"])


@pytest.mark.django_db
def test_post_auth_other(other_api_client, attachment_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.post(
        list_url(AttachmentViewSet), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    with pytest.raises(Attachment.DoesNotExist):
        Attachment.objects.get(file_name=attachment_payload["file_name"])


@pytest.mark.django_db
def test_post_auth_owner(owner_api_client, attachment_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.post(
        list_url(AttachmentViewSet), data=attachment_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "file_name" not in response.data
    with pytest.raises(Attachment.DoesNotExist):
        Attachment.objects.get(file_name=attachment_payload["file_name"])


@pytest.mark.django_db
def test_delete_noauth(fake_attachment, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.AttachmentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_attachment, other_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.delete(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_name is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_attachment, owner_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.AttachmentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.delete(detail_url(AttachmentViewSet, fake_attachment))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()
