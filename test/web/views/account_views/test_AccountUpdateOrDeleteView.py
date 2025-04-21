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

"""Test module for :mod:`web.views.account_views.AccountUpdateOrDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.AccountModel import AccountModel
from web.views.account_views.AccountUpdateOrDeleteView import AccountUpdateOrDeleteView


@pytest.mark.django_db
def test_get_noauth(accountModel, client, detail_url, login_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(AccountUpdateOrDeleteView, accountModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, accountModel)}"
    )
    assert accountModel.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(accountModel, other_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(AccountUpdateOrDeleteView, accountModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert accountModel.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(accountModel, owner_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(AccountUpdateOrDeleteView, accountModel))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "account/account_edit.html" in [t.name for t in response.templates]
    assert accountModel.mail_address in response.content.decode()
    with open("edit.html", "w") as f:
        f.write(response.content.decode())


@pytest.mark.django_db
def test_post_update_noauth(
    accountModel, accountPayload, client, detail_url, login_url
):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel), accountPayload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, accountModel)}"
    )
    accountModel.refresh_from_db()
    assert accountModel.mail_address != accountPayload["mail_address"]
    assert accountModel.password != accountPayload["password"]
    assert accountModel.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_post_update_auth_other(accountModel, accountPayload, other_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel), accountPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel.mail_address != accountPayload["mail_address"]
    assert accountModel.password != accountPayload["password"]
    assert accountModel.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_post_update_auth_owner(accountModel, accountPayload, owner_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel), accountPayload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(accountModel.get_absolute_url())
    accountModel.refresh_from_db()
    assert accountModel.mail_address == accountPayload["mail_address"]
    assert accountModel.password == accountPayload["password"]
    assert accountModel.mail_host == accountPayload["mail_host"]


@pytest.mark.django_db
def test_post_delete_noauth(accountModel, client, detail_url, login_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, accountModel)}"
    )
    accountModel.refresh_from_db()
    assert accountModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(accountModel, other_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(accountModel, owner_client, detail_url):
    """Tests :class:`web.views.account_views.AccountUpdateOrDeleteView.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountUpdateOrDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(
        reverse("web:" + AccountModel.get_list_web_url_name())
    )
    with pytest.raises(AccountModel.DoesNotExist):
        accountModel.refresh_from_db()
