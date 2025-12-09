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

"""Test module for :mod:`api.v1.views.EmailViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views import EmailViewSet
from core.models import Email


@pytest.mark.django_db
def test_list_noauth(fake_email, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(EmailViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list_auth_other(fake_email, other_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(list_url(EmailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_email, owner_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(list_url(EmailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_list_auth_admin(fake_email, admin_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(list_url(EmailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_get_noauth(fake_email, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "message_id" not in response.data


@pytest.mark.django_db
def test_get_auth_other(fake_email, other_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "message_id" not in response.data


@pytest.mark.django_db
def test_get_auth_owner(fake_email, owner_api_client, detail_url):
    """Tests the `list` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message_id"] == fake_email.message_id


@pytest.mark.django_db
def test_get_auth_admin(fake_email, admin_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "message_id" not in response.data


@pytest.mark.django_db
def test_patch_noauth(fake_email, noauth_api_client, email_payload, detail_url):
    """Tests the patch method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_patch_auth_other(fake_email, other_api_client, email_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.patch(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_patch_auth_owner(fake_email, owner_api_client, email_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_patch_auth_admin(fake_email, admin_api_client, email_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.patch(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_put_noauth(fake_email, noauth_api_client, email_payload, detail_url):
    """Tests the put method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_put_auth_other(fake_email, other_api_client, email_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.put(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_put_auth_owner(fake_email, owner_api_client, email_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_put_auth_admin(fake_email, admin_api_client, email_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.put(
        detail_url(EmailViewSet, fake_email), data=email_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    fake_email.refresh_from_db()
    assert fake_email.message_id != email_payload["message_id"]


@pytest.mark.django_db
def test_post_noauth(noauth_api_client, email_payload, list_url):
    """Tests the post method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(list_url(EmailViewSet), data=email_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "message_id" not in response.data
    with pytest.raises(Email.DoesNotExist):
        Email.objects.get(message_id=email_payload["message_id"])


@pytest.mark.django_db
def test_post_auth_other(other_api_client, email_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.post(list_url(EmailViewSet), data=email_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    with pytest.raises(Email.DoesNotExist):
        Email.objects.get(message_id=email_payload["message_id"])


@pytest.mark.django_db
def test_post_auth_owner(owner_api_client, email_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.post(list_url(EmailViewSet), data=email_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    with pytest.raises(Email.DoesNotExist):
        Email.objects.get(message_id=email_payload["message_id"])


@pytest.mark.django_db
def test_post_auth_admin(admin_api_client, email_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.post(list_url(EmailViewSet), data=email_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "message_id" not in response.data
    with pytest.raises(Email.DoesNotExist):
        Email.objects.get(message_id=email_payload["message_id"])


@pytest.mark.django_db
def test_delete_noauth(fake_email, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.EmailViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_email.refresh_from_db()
    assert fake_email.message_id is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_email, other_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.delete(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_email.refresh_from_db()
    assert fake_email.message_id is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_email, owner_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.delete(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()


@pytest.mark.django_db
def test_delete_nonexistant_auth_owner(fake_email, owner_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated owner user client.
    """
    old_id = fake_email.id
    fake_email.id = 10
    response = owner_api_client.delete(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_email.id = old_id
    fake_email.refresh_from_db()
    assert fake_email.message_id is not None


@pytest.mark.django_db
def test_delete_auth_admin(fake_email, admin_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.EmailViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.delete(detail_url(EmailViewSet, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_email.refresh_from_db()
    assert fake_email.message_id is not None
