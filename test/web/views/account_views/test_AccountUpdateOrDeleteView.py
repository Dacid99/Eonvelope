# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Test module for :mod:`web.views.AccountUpdateOrDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Account
from web.views import AccountUpdateOrDeleteView


@pytest.mark.django_db
def test_get_noauth(fake_account, client, detail_url, login_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(AccountUpdateOrDeleteView, fake_account))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, fake_account)}"
    )
    assert fake_account.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_account, other_client, detail_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(AccountUpdateOrDeleteView, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_account.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_account, owner_client, detail_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(AccountUpdateOrDeleteView, fake_account))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_edit.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "form" in response.context
    assert fake_account.mail_address in response.content.decode()


@pytest.mark.django_db
def test_post_update_noauth(
    fake_account, account_payload, client, detail_url, login_url
):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account), account_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, fake_account)}"
    )
    fake_account.refresh_from_db()
    assert fake_account.mail_address != account_payload["mail_address"]
    assert fake_account.password != account_payload["password"]
    assert fake_account.mail_host != account_payload["mail_host"]


@pytest.mark.django_db
def test_post_update_auth_other(
    fake_account, account_payload, other_client, detail_url
):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account), account_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_account.refresh_from_db()
    assert fake_account.mail_address != account_payload["mail_address"]
    assert fake_account.password != account_payload["password"]
    assert fake_account.mail_host != account_payload["mail_host"]


@pytest.mark.django_db
def test_post_update_auth_owner(
    fake_account, account_payload, owner_client, detail_url
):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account), account_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(fake_account.get_absolute_url())
    fake_account.refresh_from_db()
    assert fake_account.mail_address == account_payload["mail_address"]
    assert fake_account.password == account_payload["password"]
    assert fake_account.mail_host == account_payload["mail_host"]


@pytest.mark.django_db
def test_post_delete_noauth(fake_account, client, detail_url, login_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountUpdateOrDeleteView, fake_account)}"
    )
    fake_account.refresh_from_db()
    assert fake_account is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_account, other_client, detail_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_account.refresh_from_db()
    assert fake_account is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_account, owner_client, detail_url):
    """Tests :class:`web.views.AccountUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountUpdateOrDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Account.get_list_web_url_name()))
    with pytest.raises(Account.DoesNotExist):
        fake_account.refresh_from_db()
