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

"""Test module for :mod:`api.v1.views.AccountViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.AccountViewSet import AccountViewSet
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture
def mock_Account_update_mailboxes(mocker):
    return mocker.patch(
        "api.v1.views.AccountViewSet.Account.update_mailboxes", autospec=True
    )


@pytest.fixture
def mock_Account_test(mocker):
    return mocker.patch("api.v1.views.AccountViewSet.Account.test", autospec=True)


@pytest.mark.django_db
def test_update_mailboxes_noauth(
    fake_account,
    noauth_api_client,
    custom_detail_action_url,
    mock_Account_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, fake_account
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Account_update_mailboxes.assert_not_called()
    assert "mail_address" not in response.data


@pytest.mark.django_db
def test_update_mailboxes_auth_other(
    fake_account,
    other_api_client,
    custom_detail_action_url,
    mock_Account_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, fake_account
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Account_update_mailboxes.assert_not_called()
    assert "mail_address" not in response.data


@pytest.mark.django_db
def test_update_mailboxes_success_auth_owner(
    fake_account,
    owner_api_client,
    custom_detail_action_url,
    mock_Account_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, fake_account
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(fake_account).data
    )
    assert "error" not in response.data
    mock_Account_update_mailboxes.assert_called_once_with(fake_account)


@pytest.mark.django_db
def test_update_mailboxes_failure_auth_owner(
    faker,
    fake_account,
    owner_api_client,
    custom_detail_action_url,
    mock_Account_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Account_update_mailboxes.side_effect = MailAccountError(fake_error_message)

    response = owner_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, fake_account
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["account"] == AccountViewSet.serializer_class(fake_account).data
    )
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Account_update_mailboxes.assert_called_once_with(fake_account)


@pytest.mark.django_db
def test_test_noauth(
    fake_account,
    noauth_api_client,
    custom_detail_action_url,
    mock_Account_test,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with an unauthenticated user client."""
    previous_is_healthy = fake_account.is_healthy

    response = noauth_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, fake_account
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Account_test.assert_not_called()
    fake_account.refresh_from_db()
    assert fake_account.is_healthy is previous_is_healthy
    assert "mail_address" not in response.data


@pytest.mark.django_db
def test_test_auth_other(
    fake_account,
    other_api_client,
    custom_detail_action_url,
    mock_Account_test,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated other user client."""

    previous_is_healthy = fake_account.is_healthy

    response = other_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, fake_account
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Account_test.assert_not_called()
    fake_account.refresh_from_db()
    assert fake_account.is_healthy is previous_is_healthy
    assert "mail_address" not in response.data


@pytest.mark.django_db
def test_test_success_auth_owner(
    fake_account,
    owner_api_client,
    custom_detail_action_url,
    mock_Account_test,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated owner user client."""

    response = owner_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, fake_account
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(fake_account).data
    )
    assert response.data["result"] is True
    assert "error" not in response.data
    mock_Account_test.assert_called_once_with(fake_account)


@pytest.mark.django_db
def test_test_failure_auth_owner(
    faker,
    fake_account,
    owner_api_client,
    custom_detail_action_url,
    mock_Account_test,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Account_test.side_effect = MailAccountError(fake_error_message)

    response = owner_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, fake_account
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(fake_account).data
    )
    assert response.data["result"] is False
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Account_test.assert_called_once_with(fake_account)


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_account, noauth_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, fake_account
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_account.refresh_from_db()
    assert fake_account.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_account, other_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, fake_account
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_account.refresh_from_db()
    assert fake_account.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_account, owner_api_client, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_api_client.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, fake_account
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_account.refresh_from_db()
    assert fake_account.is_favorite is True
