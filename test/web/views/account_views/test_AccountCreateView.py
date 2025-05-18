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

"""Test module for :mod:`web.views.AccountCreateView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Account
from test.conftest import mailbox_payload
from web.views import AccountCreateView


@pytest.mark.django_db
def test_get_noauth(client, list_url, login_url):
    """Tests :class:`web.views.AccountCreateView` with an unauthenticated user client."""
    response = client.get(list_url(AccountCreateView))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(AccountCreateView)}")


@pytest.mark.django_db
def test_get_auth_other(other_client, list_url):
    """Tests :class:`web.views.AccountCreateView` with the authenticated other user client."""
    response = other_client.get(list_url(AccountCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_create.html" in [t.name for t in response.templates]
    assert "form" in response.context


@pytest.mark.django_db
def test_get_auth_owner(owner_client, list_url):
    """Tests :class:`web.views.AccountCreateView` with the authenticated owner user client."""
    response = owner_client.get(list_url(AccountCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    with open("create.html", "w") as f:
        f.write(response.content.decode())


@pytest.mark.django_db
def test_post_noauth(account_payload, client, list_url, login_url):
    """Tests :class:`web.views.AccountCreateView` with an unauthenticated user client."""
    assert Account.objects.all().count() == 1

    response = client.post(list_url(AccountCreateView), account_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(AccountCreateView)}")
    assert Account.objects.all().count() == 1


@pytest.mark.django_db
def test_post_auth_other(account_payload, other_user, other_client, list_url):
    """Tests :class:`web.views.AccountCreateView` with the authenticated other user client."""
    assert Account.objects.all().count() == 1

    response = other_client.post(list_url(AccountCreateView), account_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Account.get_list_web_url_name()))
    assert Account.objects.all().count() == 2
    added_account = Account.objects.filter(
        mail_address=account_payload["mail_address"], user=other_user
    ).get()
    assert added_account.password == account_payload["password"]
    assert added_account.mail_host == account_payload["mail_host"]
    assert added_account.mail_host_port == account_payload["mail_host_port"]


@pytest.mark.django_db
def test_post_auth_owner(account_payload, owner_user, owner_client, list_url):
    """Tests :class:`web.views.AccountCreateView` with the authenticated owner user client."""
    assert Account.objects.all().count() == 1

    response = owner_client.post(list_url(AccountCreateView), account_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Account.get_list_web_url_name()))
    assert Account.objects.all().count() == 2
    added_account = Account.objects.filter(
        mail_address=account_payload["mail_address"], user=owner_user
    ).get()
    assert added_account.password == account_payload["password"]
    assert added_account.mail_host == account_payload["mail_host"]
    assert added_account.mail_host_port == account_payload["mail_host_port"]


@pytest.mark.django_db
def test_post_duplicate_auth_owner(
    fake_account, account_payload, owner_client, list_url
):
    """Tests :class:`web.views.AccountCreateView` with the authenticated owner user client."""
    assert Account.objects.all().count() == 1

    account_payload["mail_address"] = fake_account.mail_address
    response = owner_client.post(list_url(AccountCreateView), account_payload)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert Account.objects.all().count() == 1
