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

"""Test module for :mod:`api.v1.views.AccountViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from django.forms.models import model_to_dict
from rest_framework import status

from api.v1.views import AccountViewSet
from core.models import Account


@pytest.fixture(autouse=True)
def auto_mock_Account_test(mock_Account_test):
    """All tests mock Accounts test."""


@pytest.mark.django_db
def test_list__noauth(fake_account, noauth_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AccountViewSet`
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list__auth_other(fake_account, other_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list__auth_owner(fake_account, owner_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    assert "password" not in response.data["results"][0]


@pytest.mark.django_db
def test_list__auth_admin(fake_account, admin_api_client, list_url):
    """Tests the `list` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_get__noauth(fake_account, noauth_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.AccountViewSet`
    with an unauthenticated user client.
    """
    response = noauth_api_client.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "mail_address" not in response.data


@pytest.mark.django_db
def test_get__auth_other(fake_account, other_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "password" not in response.data


@pytest.mark.django_db
def test_get__auth_owner(fake_account, owner_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == fake_account.mail_address
    assert "password" not in response.data


@pytest.mark.django_db
def test_get__auth_admin(fake_account, admin_api_client, detail_url):
    """Tests the `get` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "password" not in response.data


@pytest.mark.django_db
def test_patch__noauth(fake_account, noauth_api_client, account_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.AccountViewSet`
    with an unauthenticated user client.
    """
    response = noauth_api_client.patch(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "mail_address" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_address != account_payload["mail_address"]
    assert fake_account.password != account_payload["password"]


@pytest.mark.django_db
def test_patch__auth_other(fake_account, other_api_client, account_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.patch(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "mail_address" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_address != account_payload["mail_address"]
    assert fake_account.password != account_payload["password"]


@pytest.mark.django_db
def test_patch__auth_owner(fake_account, owner_api_client, account_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.patch(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == account_payload["mail_address"]
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_address == account_payload["mail_address"]
    assert fake_account.password == account_payload["password"]


@pytest.mark.django_db
def test_patch__auth_admin(fake_account, admin_api_client, account_payload, detail_url):
    """Tests the `patch` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.patch(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "mail_address" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_address != account_payload["mail_address"]
    assert fake_account.password != account_payload["password"]


@pytest.mark.django_db
def test_put__noauth(fake_account, noauth_api_client, account_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.AccountViewSet`
    with an unauthenticated user client.
    """
    response = noauth_api_client.put(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "mail_host" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_host != account_payload["mail_host"]


@pytest.mark.django_db
def test_put__auth_other(fake_account, other_api_client, account_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.put(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "mail_host" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_host != account_payload["mail_host"]


@pytest.mark.django_db
def test_put__auth_owner(fake_account, owner_api_client, account_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.put(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_host"] == account_payload["mail_host"]
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_host == account_payload["mail_host"]


@pytest.mark.django_db
def test_put__auth_admin(fake_account, admin_api_client, account_payload, detail_url):
    """Tests the `put` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.put(
        detail_url(AccountViewSet, fake_account), data=account_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "mail_host" not in response.data
    assert "password" not in response.data
    fake_account.refresh_from_db()
    assert fake_account.mail_host != account_payload["mail_host"]


@pytest.mark.django_db
def test_post__noauth(
    noauth_api_client, account_payload, mock_Account_update_mailboxes, list_url
):
    """Tests the `post` method on :class:`api.v1.views.AccountViewSet`
    with an unauthenticated user client.
    """
    response = noauth_api_client.post(list_url(AccountViewSet), data=account_payload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "mail_host" not in response.data
    assert "password" not in response.data
    with pytest.raises(Account.DoesNotExist):
        Account.objects.get(mail_host=account_payload["mail_host"])
    mock_Account_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post__auth_other(
    other_user,
    other_api_client,
    account_payload,
    mock_Account_update_mailboxes,
    list_url,
):
    """Tests the `post` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.post(list_url(AccountViewSet), data=account_payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == account_payload["mail_host"]
    assert "password" not in response.data
    posted_account = Account.objects.get(mail_host=account_payload["mail_host"])
    assert posted_account is not None
    assert posted_account.user == other_user
    mock_Account_update_mailboxes.assert_called_once()


@pytest.mark.django_db
def test_post__auth_owner(
    owner_user,
    owner_api_client,
    account_payload,
    mock_Account_update_mailboxes,
    list_url,
):
    """Tests the `post` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.post(list_url(AccountViewSet), data=account_payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == account_payload["mail_host"]
    assert "password" not in response.data
    posted_account = Account.objects.get(mail_host=account_payload["mail_host"])
    assert posted_account is not None
    assert posted_account.user == owner_user
    mock_Account_update_mailboxes.assert_called_once()


@pytest.mark.django_db
def test_post__duplicate__auth_owner(
    fake_account, owner_api_client, mock_Account_update_mailboxes, list_url
):
    """Tests the post method on :class:`api.v1.views.AccountViewSet` with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(fake_account)
    payload.pop("id")
    clean_payload = {key: value for key, value in payload.items() if value is not None}

    response = owner_api_client.post(list_url(AccountViewSet), data=clean_payload)

    assert response.status_code == status.HTTP_400__bad_REQUEST
    mock_Account_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post__auth_admin(
    admin_user,
    admin_api_client,
    account_payload,
    mock_Account_update_mailboxes,
    list_url,
):
    """Tests the `post` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.post(list_url(AccountViewSet), data=account_payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == account_payload["mail_host"]
    assert "password" not in response.data
    posted_account = Account.objects.get(mail_host=account_payload["mail_host"])
    assert posted_account is not None
    assert posted_account.user == admin_user
    mock_Account_update_mailboxes.assert_called_once()


@pytest.mark.django_db
def test_delete__noauth(fake_account, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_account.refresh_from_db()
    assert fake_account.mail_address is not None


@pytest.mark.django_db
def test_delete__auth_other(fake_account, other_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated other user client.
    """
    response = other_api_client.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_account.refresh_from_db()
    assert fake_account.mail_address is not None


@pytest.mark.django_db
def test_delete__auth_owner(fake_account, owner_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated owner user client.
    """
    response = owner_api_client.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Account.DoesNotExist):
        fake_account.refresh_from_db()


@pytest.mark.django_db
def test_delete__auth_admin(fake_account, admin_api_client, detail_url):
    """Tests the `delete` method on :class:`api.v1.views.AccountViewSet`
    with the authenticated admin user client.
    """
    response = admin_api_client.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_account.refresh_from_db()
    assert fake_account.mail_address is not None
