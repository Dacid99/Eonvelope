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

"""Test module for :mod:`api.v1.views.EMailViewSet`'s basic CRUD actions.

Fixtures:
    :func:`fixture_emailPayload`: Fixture creating clean :class:`core.models.EMailModel.EMailModel` payload for a patch, post or put request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.EMailViewSet import EMailViewSet
from core.models.EMailModel import EMailModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def emailPayload(mailboxModel) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.EMailModel.EMailModel` payload for a patch, post or put request.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The clean payload.
    """
    emailData = baker.prepare(EMailModel, mailbox=mailboxModel)
    payload = model_to_dict(emailData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(emailModel, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(emailModel, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(emailModel, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(emailModel, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]


@pytest.mark.django_db
def test_get_auth_other(emailModel, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["message_id"]


@pytest.mark.django_db
def test_get_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message_id"] == emailModel.message_id


@pytest.mark.django_db
def test_patch_noauth(emailModel, noauth_apiClient, emailPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_patch_auth_other(emailModel, other_apiClient, emailPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_patch_auth_owner(emailModel, owner_apiClient, emailPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_noauth(emailModel, noauth_apiClient, emailPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_auth_other(emailModel, other_apiClient, emailPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_auth_owner(emailModel, owner_apiClient, emailPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, emailPayload, list_url):
    """Tests the post method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, emailPayload, list_url):
    """Tests the post method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, emailPayload, list_url):
    """Tests the post method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_delete_noauth(emailModel, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.EMailViewSet.EMailViewSet with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None


@pytest.mark.django_db
def test_delete_auth_other(emailModel, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None


@pytest.mark.django_db
def test_delete_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(EMailModel.DoesNotExist):
        emailModel.refresh_from_db()


@pytest.mark.django_db
def test_delete_nonexistant_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.EMailViewSet.EMailViewSet with the authenticated owner user client."""
    old_id = emailModel.id
    emailModel.id = 10
    response = owner_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.id = old_id
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None
