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

"""Test module for :mod:`web.views.AccountDetailWithDeleteView`."""

import pytest
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Account
from core.utils.fetchers.exceptions import MailAccountError
from web.views import AccountFilterView
from web.views.account_views.AccountDetailWithDeleteView import (
    AccountDetailWithDeleteView,
)


@pytest.mark.django_db
def test_get_noauth(fake_account, client, detail_url, login_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(AccountDetailWithDeleteView, fake_account))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, fake_account)}"
    )
    assert fake_account.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_account, other_client, detail_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(AccountDetailWithDeleteView, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_account.mail_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_account, owner_client, detail_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(AccountDetailWithDeleteView, fake_account))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "latest_emails" in response.context
    assert isinstance(response.context["latest_emails"], QuerySet)
    assert fake_account.mail_address in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(fake_account, client, detail_url, login_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, fake_account)}"
    )
    fake_account.refresh_from_db()
    assert fake_account is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_account, other_client, detail_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_account.refresh_from_db()
    assert fake_account is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_account, owner_client, detail_url):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + AccountFilterView.URL_NAME))
    with pytest.raises(Account.DoesNotExist):
        fake_account.refresh_from_db()


@pytest.mark.django_db
def test_post_test_noauth(
    fake_account, client, detail_url, login_url, mock_Account_test
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, fake_account)}"
    )
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
def test_post_test_auth_other(
    fake_account, other_client, detail_url, mock_Account_test
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
def test_post_test_success_auth_owner(
    fake_account, owner_client, detail_url, mock_Account_test
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Account_test.assert_called_once()


@pytest.mark.django_db
def test_post_test_failure_auth_owner(
    fake_error_message, fake_account, owner_client, detail_url, mock_Account_test
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client."""
    mock_Account_test.side_effect = MailAccountError(Exception(fake_error_message))

    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Account_test.assert_called_once()
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_test_missing_action_auth_owner(
    fake_account, owner_client, detail_url, mock_Account_test
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client
    in case of the action missing in the request.
    """
    response = owner_client.post(detail_url(AccountDetailWithDeleteView, fake_account))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Account_test.assert_not_called()


@pytest.mark.django_db
def test_post_update_mailboxes_noauth(
    fake_account, client, detail_url, login_url, mock_Account_update_mailboxes
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"update_mailboxes": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AccountDetailWithDeleteView, fake_account)}"
    )
    mock_Account_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post_update_mailboxes_auth_other(
    fake_account, other_client, detail_url, mock_Account_update_mailboxes
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"update_mailboxes": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Account_update_mailboxes.assert_not_called()


@pytest.mark.django_db
def test_post_update_mailboxes_success_auth_owner(
    fake_account, owner_client, detail_url, mock_Account_update_mailboxes
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"update_mailboxes": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Account_update_mailboxes.assert_called_once()


@pytest.mark.django_db
def test_post_update_mailboxes_failure_auth_owner(
    fake_error_message,
    fake_account,
    owner_client,
    detail_url,
    mock_Account_update_mailboxes,
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Account_update_mailboxes.side_effect = MailAccountError(
        Exception(fake_error_message)
    )

    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
        {"update_mailboxes": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/account/account_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Account)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Account_update_mailboxes.assert_called_once()
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_update_mailboxes_missing_action_auth_owner(
    fake_account, owner_client, detail_url, mock_Account_update_mailboxes
):
    """Tests :class:`web.views.AccountDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(
        detail_url(AccountDetailWithDeleteView, fake_account),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Account_update_mailboxes.assert_not_called()
