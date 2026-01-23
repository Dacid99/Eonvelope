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

"""Test module for :mod:`api.v1.views.MailboxViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views import MailboxViewSet
from core.models import Mailbox


@pytest.mark.django_db
def test_list__noauth(fake_mailbox, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list__auth_other(fake_mailbox, other_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list__auth_owner(fake_mailbox, owner_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_list__auth_admin(fake_mailbox, admin_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_get__noauth(fake_mailbox, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "name" not in response.data


@pytest.mark.django_db
def test_get__auth_other(fake_mailbox, other_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get__auth_owner(fake_mailbox, owner_api_client, detail_url):
    """Tests the `list` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == fake_mailbox.name


@pytest.mark.django_db
def test_get__auth_admin(fake_mailbox, admin_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_patch__noauth(fake_mailbox, noauth_api_client, mailbox_payload, detail_url):
    """Tests the patch method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is not mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_patch__auth_other(fake_mailbox, other_api_client, mailbox_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is not mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_patch__auth_owner(fake_mailbox, owner_api_client, mailbox_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] is False
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_patch__auth_admin(fake_mailbox, admin_api_client, mailbox_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is not mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_put__noauth(fake_mailbox, noauth_api_client, mailbox_payload, detail_url):
    """Tests the put method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_put__auth_other(fake_mailbox, other_api_client, mailbox_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_put__auth_owner(fake_mailbox, owner_api_client, mailbox_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] == mailbox_payload["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments == mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_put__auth_admin(fake_mailbox, admin_api_client, mailbox_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "save_attachments" not in response.data
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]


@pytest.mark.django_db
def test_post__noauth(noauth_api_client, mailbox_payload, list_url):
    """Tests the post method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(list_url(MailboxViewSet), data=mailbox_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "save_attachments" not in response.data
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailbox_payload["save_attachments"])


@pytest.mark.django_db
def test_post__auth_other(other_api_client, mailbox_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.post(list_url(MailboxViewSet), data=mailbox_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "save_attachments" not in response.data
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailbox_payload["save_attachments"])


@pytest.mark.django_db
def test_post__auth_owner(owner_api_client, mailbox_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.post(list_url(MailboxViewSet), data=mailbox_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "save_attachments" not in response.data
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailbox_payload["save_attachments"])


@pytest.mark.django_db
def test_post__auth_admin(admin_api_client, mailbox_payload, list_url):
    """Tests the `post` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.post(list_url(MailboxViewSet), data=mailbox_payload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "save_attachments" not in response.data
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailbox_payload["save_attachments"])


@pytest.mark.django_db
def test_delete__noauth(fake_mailbox, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.name is not None


@pytest.mark.django_db
def test_delete__auth_other(fake_mailbox, other_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.name is not None


@pytest.mark.django_db
def test_delete__auth_owner(fake_mailbox, owner_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(fake_mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_delete__auth_admin(fake_mailbox, admin_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.MailboxViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.name is not None
