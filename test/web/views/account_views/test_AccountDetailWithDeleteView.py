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

"""Test module for :mod:`web.views.account_views.AccountDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.AccountModel import AccountModel
from core.utils.fetchers.exceptions import MailAccountError
from web.views.account_views.AccountDetailWithDeleteView import (
    AccountDetailWithDeleteView,
)
from web.views.account_views.AccountFilterView import AccountFilterView


@pytest.mark.django_db
def test_get_noauth(accountModel, client, detail_url, login_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(AccountDetailWithDeleteView, accountModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, accountModel)}"
    )
    assert accountModel.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(accountModel, other_client, detail_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(AccountDetailWithDeleteView, accountModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert accountModel.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(accountModel, owner_client, detail_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(AccountDetailWithDeleteView, accountModel))

    assert response.status_code == status.HTTP_200_OK
    assert accountModel.mail_address in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(accountModel, client, detail_url, login_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, accountModel)}"
    )
    accountModel.refresh_from_db()
    assert accountModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(accountModel, other_client, detail_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(accountModel, owner_client, detail_url):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + AccountFilterView.URL_NAME))
    with pytest.raises(AccountModel.DoesNotExist):
        accountModel.refresh_from_db()


@pytest.mark.django_db
def test_post_test_noauth(
    accountModel, client, detail_url, login_url, mock_AccountModel_test_connection
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, accountModel)}"
    )
    mock_AccountModel_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_auth_other(
    accountModel, other_client, detail_url, mock_AccountModel_test_connection
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_AccountModel_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_success_auth_owner(
    accountModel, owner_client, detail_url, mock_AccountModel_test_connection
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_AccountModel_test_connection.assert_called_once()


@pytest.mark.django_db
def test_post_test_failure_auth_owner(
    faker, accountModel, owner_client, detail_url, mock_AccountModel_test_connection
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_AccountModel_test_connection.side_effect = MailAccountError(fake_error_message)

    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_AccountModel_test_connection.assert_called_once()
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_update_mailboxes_noauth(
    accountModel, client, detail_url, login_url, mock_AccountModel_update_mailboxes
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"update_mailboxes": "Update Mailboxes"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, accountModel)}"
    )
    mock_AccountModel_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post_update_mailboxes_auth_other(
    accountModel, other_client, detail_url, mock_AccountModel_update_mailboxes
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"update_mailboxes": "Update Mailboxes"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_AccountModel_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post_update_mailboxes_success_auth_owner(
    accountModel, owner_client, detail_url, mock_AccountModel_update_mailboxes
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"update_mailboxes": "Update Mailboxes"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_AccountModel_update_mailboxes.assert_called_once()


@pytest.mark.django_db
def test_post_update_mailboxes_failure_auth_owner(
    accountModel, owner_client, detail_url, mock_AccountModel_update_mailboxes
):
    """Tests :class:`web.views.account_views.AccountDetailWithDeleteView.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, accountModel),
        {"update_mailboxes": "Update Mailboxes"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_AccountModel_update_mailboxes.assert_called_once()
