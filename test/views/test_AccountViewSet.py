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

"""Test module for :mod:`Emailkasten.Views.AccountViewSet`.

Fixtures:
    :func:`fixture_owner_user`: Creates a user that represents the owner of the data.
    :func:`fixture_other_user`: Creates a user that represents another user that is not the owner of the data.
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_accountPayload`: Creates clean :class:`Emailkasten.Models.AccountModel.AccountModel` payload for a post or put request.
    :func:`fixture_list_url`: Gets the viewsets url for list actions.
    :func:`fixture_detail_url`: Gets the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Gets the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Gets the viewsets url for custom detail actions.
    :func:`fixture_noauth_apiClient`: Creates an unauthenticated :class:`rest_framework.test.APIClient` instance.
    :func:`fixture_auth_other_apiClient`: Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as `other_user`.
    :func:`fixture_auth_owner_apiClient`: Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as `owner_user`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Views.AccountViewSet import AccountViewSet

if TYPE_CHECKING:
    from typing import Callable, Any


@pytest.fixture(name='accountModel')
def fixture_accountModel(owner_user) -> AccountModel:
    """Creates an :class:`Emailkasten.Models.AccountModel.AccountModel` owned by :attr:`owner_user`.

    Args:
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel, user=owner_user)

@pytest.fixture(name='accountPayload')
def fixture_accountPayload(owner_user) -> dict[str, Any]:
    """Creates clean :class:`Emailkasten.Models.AccountModel.AccountModel` payload for a post or put request.

    Args:
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The clean payload.
    """
    accountData = baker.prepare(AccountModel, user=owner_user)
    payload = model_to_dict(accountData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload

@pytest.fixture(name='list_url')
def fixture_list_url() -> str:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return reverse(f'{AccountViewSet.BASENAME}-list')

@pytest.fixture(name='detail_url')
def fixture_detail_url(accountModel) -> str:
    """Gets the viewsets url for detail actions.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The detail url."""
    return reverse(f'{AccountViewSet.BASENAME}-detail', args=[accountModel.id])

@pytest.fixture(name='custom_list_action_url')
def fixture_custom_list_action_url() -> Callable[[str],str]:
    """Gets the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda viewset, custom_list_action_url_name: reverse(f'{AccountViewSet.BASENAME}-{custom_list_action_url_name}')

@pytest.fixture(name='custom_detail_action_url')
def fixture_custom_detail_action_url(accountModel) -> Callable[[str],str]:
    """Gets the viewsets url for custom detail actions.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda custom_detail_action_url_name: reverse(f'{AccountViewSet.BASENAME}-{custom_detail_action_url_name}', args=[accountModel.id])


@pytest.mark.django_db
def test_list_noauth(accountModel, noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(accountModel, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_list_auth_owner(accountModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    with pytest.raises(KeyError):
        response.data['results'][0]['password']


@pytest.mark.django_db
def test_get_noauth(accountModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['mail_address']


@pytest.mark.django_db
def test_get_auth_other(accountModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_get_auth_owner(accountModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mail_address'] == accountModel.mail_address
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_patch_noauth(accountModel, noauth_apiClient, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(detail_url, data={'mail_address': 'test@testmail.com', 'password': 'knvolbs3yhvä234'})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['mail_address']
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_address != 'test@testmail.com'


@pytest.mark.django_db
def test_patch_auth_other(accountModel, other_apiClient, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(detail_url, data={'mail_address': 'test@testmail.com', 'password': 'knvolbs3yhvä234'})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['mail_address']
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_address != 'test@testmail.com'


@pytest.mark.django_db
def test_patch_auth_owner(accountModel, owner_apiClient, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(detail_url, data={'mail_address': 'test@testmail.com', 'password': 'knvolbs3yhvä234'})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mail_address'] == 'test@testmail.com'
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_address == 'test@testmail.com'


@pytest.mark.django_db
def test_put_noauth(accountModel, noauth_apiClient, accountPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(detail_url, data=accountPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_host != accountPayload['mail_host']


@pytest.mark.django_db
def test_put_auth_other(accountModel, other_apiClient, accountPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(detail_url, data=accountPayload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_host != accountPayload['mail_host']


@pytest.mark.django_db
def test_put_auth_owner(accountModel, owner_apiClient, accountPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(detail_url, data=accountPayload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mail_host'] == accountPayload['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    accountModel.refresh_from_db()
    assert accountModel.mail_host == accountPayload['mail_host']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, accountPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url, data=accountPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    with pytest.raises(AccountModel.DoesNotExist):
        AccountModel.objects.get(mail_host = accountPayload['mail_host'])


@pytest.mark.django_db
def test_post_auth_other(other_user, other_apiClient, accountPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url, data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['mail_host'] == accountPayload['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    postedAccountModel = AccountModel.objects.get(mail_host = accountPayload['mail_host'])
    assert postedAccountModel is not None
    assert postedAccountModel.user == other_user


@pytest.mark.django_db
def test_post_auth_owner(owner_user, owner_apiClient, accountPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url, data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['mail_host'] == accountPayload['mail_host']
    with pytest.raises(KeyError):
        response.data['password']
    postedAccountModel = AccountModel.objects.get(mail_host = accountPayload['mail_host'])
    assert postedAccountModel is not None
    assert postedAccountModel.user == owner_user


@pytest.mark.django_db
def test_post_duplicate_auth_owner(accountModel, owner_apiClient, list_url):
    """Tests the post method with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(accountModel)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}

    response = owner_apiClient.post(list_url, data=cleanPayload)

    assert cleanPayload['mail_address'] == accountModel.mail_address
    AccountModel.objects.get(mail_address = cleanPayload['mail_address'])
    assert response.status_code == status.HTTP_409_CONFLICT
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_delete_noauth(accountModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    accountModel.refresh_from_db()
    assert accountModel.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_other(accountModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(accountModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(AccountModel.DoesNotExist):
        accountModel.refresh_from_db()


@pytest.mark.django_db
def test_scan_mailboxes_noauth(accountModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.scan_mailboxes` action with an unauthenticated user client."""
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.AccountViewSet.scanMailboxes')

    response = noauth_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_scanMailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data['mail_address']


@pytest.mark.django_db
def test_scan_mailboxes_auth_other(accountModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.scan_mailboxes` action with the authenticated other user client."""
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.AccountViewSet.scanMailboxes')

    response = other_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_scanMailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data['mail_address']


@pytest.mark.django_db
def test_scan_mailboxes_auth_owner(accountModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.scan_mailboxes` action with the authenticated owner user client."""
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.AccountViewSet.scanMailboxes')

    response = owner_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['account'] == AccountViewSet.serializer_class(accountModel).data
    mock_scanMailboxes.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_test_noauth(accountModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.test` action with an unauthenticated user client."""
    mock_testAccount = mocker.patch('Emailkasten.Views.AccountViewSet.testAccount')
    previous_is_healthy = accountModel.is_healthy

    response = noauth_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_testAccount.assert_not_called()
    accountModel.refresh_from_db()
    assert accountModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['mail_address']


@pytest.mark.django_db
def test_test_auth_other(accountModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.test` action with the authenticated other user client."""
    mock_testAccount = mocker.patch('Emailkasten.Views.AccountViewSet.testAccount')
    previous_is_healthy = accountModel.is_healthy

    response = other_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_testAccount.assert_not_called()
    accountModel.refresh_from_db()
    assert accountModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['mail_address']

@pytest.mark.django_db
def test_test_auth_owner(accountModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.test` action with the authenticated owner user client."""
    mock_testAccount = mocker.patch('Emailkasten.Views.AccountViewSet.testAccount')

    response = owner_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['account'] == AccountViewSet.serializer_class(accountModel).data
    mock_testAccount.assert_called_once_with(accountModel)


@pytest.mark.django_db
def test_toggle_favorite_noauth(accountModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(accountModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(accountModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AccountViewSet.AccountViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(custom_detail_action_url(AccountViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_200_OK
    accountModel.refresh_from_db()
    assert accountModel.is_favorite is True
