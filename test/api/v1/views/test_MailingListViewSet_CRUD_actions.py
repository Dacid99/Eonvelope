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

"""Test module for :mod:`api.v1.views.MailingListViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views import MailingListViewSet
from core.models import MailingList


@pytest.mark.django_db
def test_list_noauth(fake_mailing_list, fake_email, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list_auth_other(fake_mailing_list, fake_email, other_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_mailing_list, fake_email, owner_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(fake_mailing_list, fake_email, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(detail_url(MailingListViewSet, fake_mailing_list))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "list_id" not in response.data


@pytest.mark.django_db
def test_get_auth_other(fake_mailing_list, fake_email, other_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.get(detail_url(MailingListViewSet, fake_mailing_list))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "list_id" not in response.data


@pytest.mark.django_db
def test_get_auth_owner(fake_mailing_list, fake_email, owner_api_client, detail_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.get(detail_url(MailingListViewSet, fake_mailing_list))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["list_id"] == fake_mailing_list.list_id


@pytest.mark.django_db
def test_patch_noauth(
    fake_mailing_list, fake_email, noauth_api_client, mailing_list_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_patch_auth_other(
    fake_mailing_list, fake_email, other_api_client, mailing_list_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.patch(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_patch_auth_owner(
    fake_mailing_list, fake_email, owner_api_client, mailing_list_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.patch(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_put_noauth(
    fake_mailing_list, fake_email, noauth_api_client, mailing_list_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_put_auth_other(
    fake_mailing_list, fake_email, other_api_client, mailing_list_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.put(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_put_auth_owner(
    fake_mailing_list, fake_email, owner_api_client, mailing_list_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.put(
        detail_url(MailingListViewSet, fake_mailing_list), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id != mailing_list_payload["list_id"]


@pytest.mark.django_db
def test_post_noauth(noauth_api_client, mailing_list_payload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(
        list_url(MailingListViewSet), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "list_id" not in response.data
    with pytest.raises(MailingList.DoesNotExist):
        MailingList.objects.get(list_id=mailing_list_payload["list_id"])


@pytest.mark.django_db
def test_post_auth_other(other_api_client, mailing_list_payload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.post(
        list_url(MailingListViewSet), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    with pytest.raises(MailingList.DoesNotExist):
        MailingList.objects.get(list_id=mailing_list_payload["list_id"])


@pytest.mark.django_db
def test_post_auth_owner(owner_api_client, mailing_list_payload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.post(
        list_url(MailingListViewSet), data=mailing_list_payload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "list_id" not in response.data
    with pytest.raises(MailingList.DoesNotExist):
        MailingList.objects.get(list_id=mailing_list_payload["list_id"])


@pytest.mark.django_db
def test_delete_noauth(fake_mailing_list, fake_email, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(
        detail_url(MailingListViewSet, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_mailing_list, fake_email, other_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet` with the authenticated other user client."""
    response = other_api_client.delete(
        detail_url(MailingListViewSet, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_mailing_list, fake_email, owner_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    response = owner_api_client.delete(
        detail_url(MailingListViewSet, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(MailingList.DoesNotExist):
        fake_mailing_list.refresh_from_db()


@pytest.mark.django_db
def test_delete_nonexistant_auth_owner(
    fake_mailing_list, fake_email, owner_api_client, detail_url
):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet` with the authenticated owner user client."""
    old_id = fake_mailing_list.id
    fake_mailing_list.id = 10
    response = owner_api_client.delete(
        detail_url(MailingListViewSet, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailing_list.id = old_id
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list.list_id is not None
