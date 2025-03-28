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

"""Test module for :mod:`api.v1.views.CorrespondentViewSet`'s basic CRUD actions.

Fixtures:
    :func:`fixture_correspondentPayload`: Fixture creating clean :class:`core.models.CorrespondentModel.CorrespondentModel` payload for a patch, post or put request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.serializers.correspondent_serializers.BaseCorrespondentSerializer import (
    BaseCorrespondentSerializer,
)
from api.v1.views.CorrespondentViewSet import CorrespondentViewSet
from core.models.CorrespondentModel import CorrespondentModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def correspondentPayload(emailModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.CorrespondentModel.CorrespondentModel` payload for a patch, post or put request.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The clean payload.
    """
    correspondentData = baker.prepare(CorrespondentModel, emails=[emailModel])
    payload = model_to_dict(correspondentData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(correspondentModel, emailModel, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(correspondentModel, emailModel, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(correspondentModel, emailModel, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == [
        BaseCorrespondentSerializer(correspondentModel).data
    ]
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(correspondentModel, emailModel, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_address"]


@pytest.mark.django_db
def test_get_auth_other(correspondentModel, emailModel, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.get(detail_url(CorrespondentViewSet, correspondentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["email_address"]


@pytest.mark.django_db
def test_get_auth_owner(correspondentModel, emailModel, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(CorrespondentViewSet, correspondentModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_address"] == correspondentModel.email_address


@pytest.mark.django_db
def test_patch_noauth(
    correspondentModel, emailModel, noauth_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_patch_auth_other(
    correspondentModel, emailModel, other_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_patch_auth_owner(
    correspondentModel, emailModel, owner_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_put_noauth(
    correspondentModel, emailModel, noauth_apiClient, correspondentPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_put_auth_other(
    correspondentModel, emailModel, other_apiClient, correspondentPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_put_auth_owner(
    correspondentModel, emailModel, owner_apiClient, correspondentPayload, detail_url
):
    """Tests the put method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(CorrespondentViewSet, correspondentModel), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address != correspondentPayload["email_address"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, correspondentPayload, list_url):
    """Tests the post method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.post(
        list_url(CorrespondentViewSet), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_address"]
    with pytest.raises(CorrespondentModel.DoesNotExist):
        CorrespondentModel.objects.get(
            email_address=correspondentPayload["email_address"]
        )


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, correspondentPayload, list_url):
    """Tests the post method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.post(
        list_url(CorrespondentViewSet), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    with pytest.raises(CorrespondentModel.DoesNotExist):
        CorrespondentModel.objects.get(
            email_address=correspondentPayload["email_address"]
        )


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, correspondentPayload, list_url):
    """Tests the post method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.post(
        list_url(CorrespondentViewSet), data=correspondentPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_address"]
    with pytest.raises(CorrespondentModel.DoesNotExist):
        CorrespondentModel.objects.get(
            email_address=correspondentPayload["email_address"]
        )


@pytest.mark.django_db
def test_delete_noauth(correspondentModel, emailModel, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with an unauthenticated user client."""
    response = noauth_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None


@pytest.mark.django_db
def test_delete_auth_other(correspondentModel, emailModel, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated other user client."""
    response = other_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(correspondentModel, emailModel, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet with the authenticated owner user client."""
    response = owner_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None
