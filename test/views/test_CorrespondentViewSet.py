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

"""Test module for :mod:`api.v1.views.CorrespondentViewSet`.

Fixtures:
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_correspondentModel`: Creates an email in `accountModel`.
    :func:`fixture_correspondentPayload`: Creates clean :class:`core.models.CorrespondentModel.CorrespondentModel` payload for a patch, post or put request.

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

from .test_AccountViewSet import fixture_accountModel
from .test_EMailViewSet import fixture_emailModel
from .test_MailboxViewSet import fixture_mailboxModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture(name="correspondentModel", autouse=True)
def fixture_correspondentModel(emailModel) -> CorrespondentModel:
    """Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` owned by :attr:`owner_user`.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.fixture(name="correspondentPayload")
def fixture_correspondentPayload(emailModel) -> dict[str, Any]:
    """Creates clean :class:`core.models.CorrespondentModel.CorrespondentModel` payload for a patch, post or put request.

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
def test_list_noauth(noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(correspondentModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(CorrespondentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"] == [
        BaseCorrespondentSerializer(correspondentModel).data
    ]
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(correspondentModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_address"]


@pytest.mark.django_db
def test_get_auth_other(correspondentModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(CorrespondentViewSet, correspondentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["email_address"]


@pytest.mark.django_db
def test_get_auth_owner(correspondentModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(CorrespondentViewSet, correspondentModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_address"] == correspondentModel.email_address


@pytest.mark.django_db
def test_patch_noauth(
    correspondentModel, noauth_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method with an unauthenticated user client."""
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
    correspondentModel, other_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method with the authenticated other user client."""
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
    correspondentModel, owner_apiClient, correspondentPayload, detail_url
):
    """Tests the patch method with the authenticated owner user client."""
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
    correspondentModel, noauth_apiClient, correspondentPayload, detail_url
):
    """Tests the put method with an unauthenticated user client."""
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
    correspondentModel, other_apiClient, correspondentPayload, detail_url
):
    """Tests the put method with the authenticated other user client."""
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
    correspondentModel, owner_apiClient, correspondentPayload, detail_url
):
    """Tests the put method with the authenticated owner user client."""
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
    """Tests the post method with an unauthenticated user client."""
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
    """Tests the post method with the authenticated other user client."""
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
    """Tests the post method with the authenticated owner user client."""
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
def test_delete_noauth(correspondentModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None


@pytest.mark.django_db
def test_delete_auth_other(correspondentModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(correspondentModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(
        detail_url(CorrespondentViewSet, correspondentModel)
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    correspondentModel.refresh_from_db()
    assert correspondentModel.email_address is not None


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    correspondentModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            correspondentModel,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    correspondentModel.refresh_from_db()
    assert correspondentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    correspondentModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            correspondentModel,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    correspondentModel.refresh_from_db()
    assert correspondentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    correspondentModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.CorrespondentViewSet.CorrespondentViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            CorrespondentViewSet,
            CorrespondentViewSet.URL_NAME_TOGGLE_FAVORITE,
            correspondentModel,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    correspondentModel.refresh_from_db()
    assert correspondentModel.is_favorite is True
