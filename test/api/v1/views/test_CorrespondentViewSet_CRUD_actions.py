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

"""Test module for :mod:`api.v1.views.CorrespondentViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.serializers.correspondent_serializers.BaseCorrespondentSerializer import (
    BaseCorrespondentSerializer,
)
from api.v1.views import CorrespondentViewSet
from core.models import Correspondent


@pytest.mark.django_db
def test_list_noauth(fake_correspondent, fake_email, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list_auth_other(fake_correspondent, fake_email, other_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_correspondent, fake_email, owner_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == [
        BaseCorrespondentSerializer(fake_correspondent).data
    ]
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_list_auth_admin(fake_correspondent, fake_email, admin_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_get_noauth(fake_correspondent, fake_email, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_address" not in response.data


@pytest.mark.django_db
def test_get_auth_other(fake_correspondent, fake_email, other_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "email_address" not in response.data


@pytest.mark.django_db
def test_get_auth_owner(fake_correspondent, fake_email, owner_api_client, detail_url):
    """Tests the `list` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_address"] == fake_correspondent.email_address


@pytest.mark.django_db
def test_get_auth_admin(fake_correspondent, fake_email, admin_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "email_address" not in response.data


@pytest.mark.django_db
def test_patch_noauth(
    fake_correspondent, fake_email, noauth_api_client, correspondent_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_patch_auth_other(
    fake_correspondent, fake_email, other_api_client, correspondent_payload, detail_url
):
    """Tests the `patch` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.patch(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_patch_auth_owner(
    fake_correspondent, fake_email, owner_api_client, correspondent_payload, detail_url
):
    """Tests the `patch` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_patch_auth_admin(
    fake_correspondent, fake_email, admin_api_client, correspondent_payload, detail_url
):
    """Tests the `patch` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.patch(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_put_noauth(
    fake_correspondent, fake_email, noauth_api_client, correspondent_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_put_auth_other(
    fake_correspondent, fake_email, other_api_client, correspondent_payload, detail_url
):
    """Tests the `put` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.put(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_put_auth_owner(
    fake_correspondent, fake_email, owner_api_client, correspondent_payload, detail_url
):
    """Tests the `put` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_put_auth_admin(
    fake_correspondent, fake_email, admin_api_client, correspondent_payload, detail_url
):
    """Tests the `put` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.put(
        detail_url(CorrespondentViewSet, fake_correspondent), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address != correspondent_payload["email_address"]


@pytest.mark.django_db
def test_post_noauth(noauth_api_client, correspondent_payload, list_url):
    """Tests the post method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(
        list_url(CorrespondentViewSet), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_address" not in response.data
    with pytest.raises(Correspondent.DoesNotExist):
        Correspondent.objects.get(email_address=correspondent_payload["email_address"])


@pytest.mark.django_db
def test_post_auth_other(other_api_client, correspondent_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.post(
        list_url(CorrespondentViewSet), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    with pytest.raises(Correspondent.DoesNotExist):
        Correspondent.objects.get(email_address=correspondent_payload["email_address"])


@pytest.mark.django_db
def test_post_auth_owner(owner_api_client, correspondent_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.post(
        list_url(CorrespondentViewSet), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    with pytest.raises(Correspondent.DoesNotExist):
        Correspondent.objects.get(email_address=correspondent_payload["email_address"])


@pytest.mark.django_db
def test_post_auth_admin(admin_api_client, correspondent_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.post(
        list_url(CorrespondentViewSet), data=correspondent_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_address" not in response.data
    with pytest.raises(Correspondent.DoesNotExist):
        Correspondent.objects.get(email_address=correspondent_payload["email_address"])


@pytest.mark.django_db
def test_delete_noauth(fake_correspondent, fake_email, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.CorrespondentViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address is not None


@pytest.mark.django_db
def test_delete_auth_other(
    fake_correspondent, fake_email, other_api_client, detail_url
):
    """Tests the `delete` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.delete(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(
    fake_correspondent, fake_email, owner_api_client, detail_url
):
    """Tests the `delete` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.delete(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Correspondent.DoesNotExist):
        fake_correspondent.refresh_from_db()


@pytest.mark.django_db
def test_delete_auth_admin(
    fake_correspondent, fake_email, admin_api_client, detail_url
):
    """Tests the `delete` method on :class:`api.v1.views.CorrespondentViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.delete(
        detail_url(CorrespondentViewSet, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_correspondent.refresh_from_db()
    assert fake_correspondent.email_address is not None
