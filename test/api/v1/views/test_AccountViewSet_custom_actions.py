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

"""Test module for :mod:`api.v1.views.AccountViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.AccountViewSet import AccountViewSet
from core.utils.fetchers.exceptions import MailAccountError


@pytest.fixture(name="mock_AccountModel_update_mailboxes")
def fixture_mock_AccountModel_update_mailboxes(mocker):
    return mocker.patch(
        "api.v1.views.AccountViewSet.AccountModel.update_mailboxes", autospec=True
    )


@pytest.fixture(name="mock_AccountModel_test_connection")
def fixture_mock_AccountModel_test_connection(mocker):
    return mocker.patch(
        "api.v1.views.AccountViewSet.AccountModel.test_connection", autospec=True
    )


@pytest.mark.django_db
def test_update_mailboxes_noauth(
    accountModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_AccountModel_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, accountModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_AccountModel_update_mailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_update_mailboxes_auth_other(
    accountModel,
    other_apiClient,
    custom_detail_action_url,
    mock_AccountModel_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, accountModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_AccountModel_update_mailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_update_mailboxes_success_auth_owner(
    accountModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_AccountModel_update_mailboxes,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, accountModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(accountModel).data
    )
    assert "error" not in response.data
    mock_AccountModel_update_mailboxes.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_update_mailboxes_failure_auth_owner(
    faker,
    accountModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_AccountModel_update_mailboxes,
):
    fake_error_message = faker.sentence()
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.update_mailboxes` action with the authenticated owner user client."""
    mock_AccountModel_update_mailboxes.side_effect = MailAccountError(
        fake_error_message
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_UPDATE_MAILBOXES, accountModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["account"] == AccountViewSet.serializer_class(accountModel).data
    )
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_AccountModel_update_mailboxes.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_test_noauth(
    accountModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_AccountModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with an unauthenticated user client."""
    previous_is_healthy = accountModel.is_healthy

    response = noauth_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, accountModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_AccountModel_test_connection.assert_not_called()
    accountModel.refresh_from_db()
    assert accountModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_test_auth_other(
    accountModel,
    other_apiClient,
    custom_detail_action_url,
    mock_AccountModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated other user client."""

    previous_is_healthy = accountModel.is_healthy

    response = other_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, accountModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_AccountModel_test_connection.assert_not_called()
    accountModel.refresh_from_db()
    assert accountModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_test_success_auth_owner(
    accountModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_AccountModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated owner user client."""

    response = owner_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, accountModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(accountModel).data
    )
    assert response.data["result"] is True
    assert "error" not in response.data
    mock_AccountModel_test_connection.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_test_failure_auth_owner(
    faker,
    accountModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_AccountModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.test` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_AccountModel_test_connection.side_effect = MailAccountError(fake_error_message)

    response = owner_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TEST, accountModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["account"] == AccountViewSet.serializer_class(accountModel).data
    )
    assert response.data["result"] is False
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_AccountModel_test_connection.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    accountModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, accountModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    accountModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, accountModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    accountModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            AccountViewSet, AccountViewSet.URL_NAME_TOGGLE_FAVORITE, accountModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is True
