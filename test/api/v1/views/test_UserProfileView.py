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

"""Test module for :mod:`api.v1.views.UserProfileView`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from django.forms.models import model_to_dict
from rest_framework import status

from api.v1.views import UserProfileView


@pytest.mark.django_db
def test_get_noauth(noauth_api_client, url):
    """Tests the `get` method on :class:`api.v1.views.UserProfileView`
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(url(UserProfileView))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "paperless_url" not in response.data


@pytest.mark.django_db
def test_get_auth_other(other_api_client, url):
    """Tests the `get` method on :class:`api.v1.views.UserProfileView`
    with the authenticated other user client.
    """
    response = other_api_client.get(url(UserProfileView))

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert (
        response.data["paperless_url"]
        == other_api_client.handler._force_user.profile.paperless_url
    )
    assert "paperless_api_key" not in response.data


@pytest.mark.django_db
def test_get_auth_owner(owner_api_client, url):
    """Tests the `get` method on :class:`api.v1.views.UserProfileView`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(url(UserProfileView))

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert (
        response.data["paperless_url"]
        == owner_api_client.handler._force_user.profile.paperless_url
    )
    assert "paperless_api_key" not in response.data


@pytest.mark.django_db
def test_get_auth_admin(admin_api_client, url):
    """Tests the `get` method on :class:`api.v1.views.UserProfileView`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(url(UserProfileView))

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert (
        response.data["paperless_url"]
        == admin_api_client.handler._force_user.profile.paperless_url
    )
    assert "paperless_api_key" not in response.data


@pytest.mark.django_db
def test_patch_noauth(noauth_api_client, profile_payload, url):
    """Tests the `patch` method on :class:`api.v1.views.UserProfileView`
    with an unauthenticated user client.
    """
    response = noauth_api_client.patch(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "paperless_url" not in response.data
    assert "paperless_api_key" not in response.data


@pytest.mark.django_db
def test_patch_auth_other(other_api_client, profile_payload, url):
    """Tests the `patch` method on :class:`api.v1.views.UserProfileView`
    with the authenticated other user client.
    """
    response = other_api_client.patch(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    other_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        other_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )
    assert (
        other_api_client.handler._force_user.profile.paperless_api_key
        == profile_payload["paperless_api_key"]
    )


@pytest.mark.django_db
def test_patch_auth_owner(owner_api_client, profile_payload, url):
    """Tests the `patch` method on :class:`api.v1.views.UserProfileView`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    owner_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        owner_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )
    assert (
        owner_api_client.handler._force_user.profile.paperless_api_key
        == profile_payload["paperless_api_key"]
    )


@pytest.mark.django_db
def test_patch_auth_admin(admin_api_client, profile_payload, url):
    """Tests the `patch` method on :class:`api.v1.views.UserProfileView`
    with the authenticated admin user client.
    """
    response = admin_api_client.patch(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    admin_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        admin_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )
    assert (
        admin_api_client.handler._force_user.profile.paperless_api_key
        == profile_payload["paperless_api_key"]
    )


@pytest.mark.django_db
def test_put_noauth(noauth_api_client, profile_payload, url):
    """Tests the `put` method on :class:`api.v1.views.UserProfileView`
    with an unauthenticated user client.
    """
    response = noauth_api_client.put(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "paperless_url" not in response.data
    assert "paperless_api_key" not in response.data


@pytest.mark.django_db
def test_put_auth_other(other_api_client, profile_payload, url):
    """Tests the `put` method on :class:`api.v1.views.UserProfileView`
    with the authenticated other user client.
    """
    response = other_api_client.put(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    other_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        other_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )


@pytest.mark.django_db
def test_put_auth_owner(owner_api_client, profile_payload, url):
    """Tests the `put` method on :class:`api.v1.views.UserProfileView`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    owner_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        owner_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )


@pytest.mark.django_db
def test_put_auth_admin(admin_api_client, profile_payload, url):
    """Tests the `put` method on :class:`api.v1.views.UserProfileView`
    with the authenticated admin user client.
    """
    response = admin_api_client.put(url(UserProfileView), data=profile_payload)

    assert response.status_code == status.HTTP_200_OK
    assert "paperless_url" in response.data
    assert response.data["paperless_url"] == profile_payload["paperless_url"]
    assert "paperless_api_key" not in response.data
    admin_api_client.handler._force_user.profile.refresh_from_db()
    assert (
        admin_api_client.handler._force_user.profile.paperless_url
        == profile_payload["paperless_url"]
    )
