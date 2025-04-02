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

from api.v1.views.MailingListViewSet import MailingListViewSet
from core.models.MailingListModel import MailingListModel


@pytest.mark.django_db
def test_list_noauth(mailingListModel, emailModel, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(mailingListModel, emailModel, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(mailingListModel, emailModel, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(MailingListViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(mailingListModel, emailModel, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["list_id"]


@pytest.mark.django_db
def test_get_auth_other(mailingListModel, emailModel, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.get(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["list_id"]


@pytest.mark.django_db
def test_get_auth_owner(mailingListModel, emailModel, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["list_id"] == mailingListModel.list_id


@pytest.mark.django_db
def test_patch_noauth(
    mailingListModel, emailModel, noauth_apiClient, mailingListPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_patch_auth_other(
    mailingListModel, emailModel, other_apiClient, mailingListPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_patch_auth_owner(
    mailingListModel, emailModel, owner_apiClient, mailingListPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_put_noauth(
    mailingListModel, emailModel, noauth_apiClient, mailingListPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_put_auth_other(
    mailingListModel, emailModel, other_apiClient, mailingListPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_put_auth_owner(
    mailingListModel, emailModel, owner_apiClient, mailingListPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(MailingListViewSet, mailingListModel), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id != mailingListPayload["list_id"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailingListPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.post(
        list_url(MailingListViewSet), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["list_id"]
    with pytest.raises(MailingListModel.DoesNotExist):
        MailingListModel.objects.get(list_id=mailingListPayload["list_id"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, mailingListPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.post(
        list_url(MailingListViewSet), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    with pytest.raises(MailingListModel.DoesNotExist):
        MailingListModel.objects.get(list_id=mailingListPayload["list_id"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailingListPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.post(
        list_url(MailingListViewSet), data=mailingListPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["list_id"]
    with pytest.raises(MailingListModel.DoesNotExist):
        MailingListModel.objects.get(list_id=mailingListPayload["list_id"])


@pytest.mark.django_db
def test_delete_noauth(mailingListModel, emailModel, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id is not None


@pytest.mark.django_db
def test_delete_auth_other(mailingListModel, emailModel, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id is not None


@pytest.mark.django_db
def test_delete_auth_owner(mailingListModel, emailModel, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(MailingListModel.DoesNotExist):
        mailingListModel.refresh_from_db()


@pytest.mark.django_db
def test_delete_nonexistant_auth_owner(
    mailingListModel, emailModel, owner_apiClient, detail_url
):
    """Tests the delete method on :class:`api.v1.views.MailingListViewSet.MailingListViewSet with the authenticated owner user client."""
    old_id = mailingListModel.id
    mailingListModel.id = 10
    response = owner_apiClient.delete(detail_url(MailingListViewSet, mailingListModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailingListModel.id = old_id
    mailingListModel.refresh_from_db()
    assert mailingListModel.list_id is not None
