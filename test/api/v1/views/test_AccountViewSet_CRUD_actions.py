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

"""Test module for :mod:`api.v1.views.AccountViewSet`'s basic CRUD actions.

Fixtures:
    :func:`fixture_accountPayload`: Fixture creating clean :class:`core.models.AccountModel.AccountModel` payload for a patch, post or put request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.AccountViewSet import AccountViewSet
from core.models.AccountModel import AccountModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def accountPayload(owner_user) -> dict[str, Any]:
    """Fixture creating clean :class:`core.models.AccountModel.AccountModel` payload for a patch, post or put request.

    Args:
        owner_user: Depends on :func:`owner_user`.

    Returns:
        The clean payload.
    """
    accountData = baker.prepare(AccountModel, user=owner_user)
    payload = model_to_dict(accountData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(accountModel, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(accountModel, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(accountModel, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    with pytest.raises(KeyError):
        response.data["results"][0]["password"]


@pytest.mark.django_db
def test_get_noauth(accountModel, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_get_auth_other(accountModel, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.get(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["password"]


@pytest.mark.django_db
def test_get_auth_owner(accountModel, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == accountModel.mail_address
    with pytest.raises(KeyError):
        response.data["password"]


@pytest.mark.django_db
def test_patch_noauth(accountModel, noauth_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_address != accountPayload["mail_address"]
    assert accountModel.password != accountPayload["password"]


@pytest.mark.django_db
def test_patch_auth_other(accountModel, other_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_address != accountPayload["mail_address"]
    assert accountModel.password != accountPayload["password"]


@pytest.mark.django_db
def test_patch_auth_owner(accountModel, owner_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == accountPayload["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_address == accountPayload["mail_address"]
    assert accountModel.password == accountPayload["password"]


@pytest.mark.django_db
def test_put_noauth(accountModel, noauth_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_put_auth_other(accountModel, other_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_put_auth_owner(accountModel, owner_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(AccountViewSet, accountModel), data=accountPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    accountModel.refresh_from_db()
    assert accountModel.mail_host == accountPayload["mail_host"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    with pytest.raises(AccountModel.DoesNotExist):
        AccountModel.objects.get(mail_host=accountPayload["mail_host"])


@pytest.mark.django_db
def test_post_auth_other(other_user, other_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    postedAccountModel = AccountModel.objects.get(mail_host=accountPayload["mail_host"])
    assert postedAccountModel is not None
    assert postedAccountModel.user == other_user


@pytest.mark.django_db
def test_post_auth_owner(owner_user, owner_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    postedAccountModel = AccountModel.objects.get(mail_host=accountPayload["mail_host"])
    assert postedAccountModel is not None
    assert postedAccountModel.user == owner_user


@pytest.mark.django_db
def test_post_duplicate_auth_owner(accountModel, owner_apiClient, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(accountModel)
    payload.pop("id")
    cleanPayload = {key: value for key, value in payload.items() if value is not None}

    response = owner_apiClient.post(list_url(AccountViewSet), data=cleanPayload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_noauth(accountModel, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    accountModel.refresh_from_db()
    assert accountModel.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_other(accountModel, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(accountModel, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(AccountViewSet, accountModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(AccountModel.DoesNotExist):
        accountModel.refresh_from_db()
