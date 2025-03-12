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

"""Test module for :mod:`api.v1.views.DaemonViewSet`'s basic CRUD actions.

Fixtures:
    :func:`fixture_daemonPayload`: Creates clean :class:`core.models.DaemonModel.DaemonModel` payload for a patch, post or put request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.DaemonViewSet import DaemonViewSet
from core.models.DaemonModel import DaemonModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def daemonPayload(faker, mailboxModel) -> dict[str, Any]:
    """Creates clean :class:`core.models.DaemonModel.DaemonModel` payload for a patch, post or put request.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The clean payload.
    """
    mailboxData = baker.prepare(
        DaemonModel,
        mailbox=mailboxModel,
        log_filepath=faker.file_path(extension="log"),
        cycle_interval=1234,
    )
    payload = model_to_dict(mailboxData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]


@pytest.mark.django_db
def test_get_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonModel.cycle_interval


@pytest.mark.django_db
def test_patch_noauth(daemonModel, noauth_apiClient, daemonPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_patch_auth_other(daemonModel, other_apiClient, daemonPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_patch_auth_owner(daemonModel, owner_apiClient, daemonPayload, detail_url):
    """Tests the patch method with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonPayload["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval == daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_noauth(daemonModel, noauth_apiClient, daemonPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_auth_other(daemonModel, other_apiClient, daemonPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_auth_owner(daemonModel, owner_apiClient, daemonPayload, detail_url):
    """Tests the put method with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonPayload["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval == daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, daemonPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, daemonPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, daemonPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_delete_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval is not None


@pytest.mark.django_db
def test_delete_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval is not None


@pytest.mark.django_db
def test_delete_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(daemonModel.DoesNotExist):
        daemonModel.refresh_from_db()
