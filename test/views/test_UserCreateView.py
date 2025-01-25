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

"""Test module for :mod:`api.views.UserViewSet`.

Fixtures:
    :func:`fixture_owner_user`: Creates an account owned by `owner_user`.
    :func:`fixture_userPayload`: Creates clean :class:`core.models.User.User` payload for a patch, post or put request.
    :func:`fixture_list_url`: Gets the viewsets url for list actions.
    :func:`fixture_detail_url`: Gets the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Gets the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Gets the viewsets url for custom detail actions.
"""

from __future__ import annotations

import pytest
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from rest_framework.test import APIClient
from model_bakery import baker
from rest_framework import status

from api.views.UserViewSet import UserViewSet

@pytest.fixture(name='admin_user')
def fixture_admin_user() -> User:
    """Creates a :class:`django.contrib.auth.models.User`
    that represents another user that is not the owner of the data.
    Invoked as other_user.

    Returns:
       The other user instance.
    """
    return baker.make(User, is_staff=True)


@pytest.fixture(name='admin_apiClient')
def fixture_admin_apiClient(noauth_apiClient, admin_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance
    that is authenticated as :attr:`other_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        admin_user: Depends on :func:`fixture_admin_user`.

    Returns:
        The authenticated admin APIClient.
    """
    noauth_apiClient.force_authenticate(user=admin_user)
    return noauth_apiClient


@pytest.fixture(name="userPayload")
def fixture_userPayload():
    userData = baker.prepare(User, is_staff=False)
    payload = model_to_dict(userData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload


@pytest.mark.django_db
def test_list_noauth(noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(UserViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(owner_user, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(UserViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    with pytest.raises(KeyError):
        response.data['results'][0]['password']


@pytest.mark.django_db
def test_list_auth_owner(other_user, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(UserViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1
    with pytest.raises(KeyError):
        response.data['results'][0]['password']


@pytest.mark.django_db
def test_get_noauth(owner_user, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_get_auth_other(owner_user, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_get_auth_owner(owner_user, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == owner_user.username
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_get_auth_admin(owner_user, admin_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = admin_apiClient.get(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == owner_user.username
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_patch_noauth(owner_user, noauth_apiClient, userPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username != userPayload['username']


@pytest.mark.django_db
def test_patch_auth_other(owner_user, other_apiClient, userPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username != userPayload['username']


@pytest.mark.django_db
def test_patch_auth_owner(owner_user, owner_apiClient, userPayload, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == userPayload['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username == userPayload['username']


@pytest.mark.django_db
def test_put_noauth(owner_user, noauth_apiClient, userPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username != userPayload['username']


@pytest.mark.django_db
def test_put_auth_other(owner_user, other_apiClient, userPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username != userPayload['username']


@pytest.mark.django_db
def test_put_auth_owner(owner_user, owner_apiClient, userPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == userPayload['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username == userPayload['username']


@pytest.mark.django_db
def test_put_auth_admin(owner_user, admin_apiClient, userPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = admin_apiClient.put(detail_url(UserViewSet, owner_user), data=userPayload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == userPayload['username']
    with pytest.raises(KeyError):
        response.data['password']
    owner_user.refresh_from_db()
    assert owner_user.username == userPayload['username']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, userPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(UserViewSet), data=userPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['username']
    with pytest.raises(KeyError):
        response.data['password']
    with pytest.raises(User.DoesNotExist):
        User.objects.get(username = userPayload['username'])


@pytest.mark.django_db
def test_post_auth_other(other_user, other_apiClient, userPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(UserViewSet), data=userPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == userPayload['username']
    with pytest.raises(KeyError):
        response.data['password']
    postedUser = User.objects.get(username = userPayload['username'])
    assert postedUser is not None
    assert postedUser.user == other_user


@pytest.mark.django_db
def test_post_auth_owner(owner_user, owner_apiClient, userPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(UserViewSet), data=userPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == userPayload['username']
    with pytest.raises(KeyError):
        response.data['password']
    postedUser = User.objects.get(username = userPayload['username'])
    assert postedUser is not None
    assert postedUser.user == owner_user


@pytest.mark.django_db
def test_post_duplicate_auth_owner(owner_user, owner_apiClient, list_url):
    """Tests the post method with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(owner_user)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}

    response = owner_apiClient.post(list_url(UserViewSet), data=cleanPayload)

    assert cleanPayload['username'] == owner_user.username
    User.objects.get(username = cleanPayload['username'])
    assert response.status_code == status.HTTP_409_CONFLICT
    with pytest.raises(KeyError):
        response.data['password']


@pytest.mark.django_db
def test_delete_noauth(owner_user, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    owner_user.refresh_from_db()
    assert owner_user.username is not None


@pytest.mark.django_db
def test_delete_auth_other(owner_user, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    owner_user.refresh_from_db()
    assert owner_user.username is not None


@pytest.mark.django_db
def test_delete_auth_owner(owner_user, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(User.DoesNotExist):
        owner_user.refresh_from_db()


@pytest.mark.django_db
def test_delete_auth_admin(owner_user, admin_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = admin_apiClient.delete(detail_url(UserViewSet, owner_user))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(User.DoesNotExist):
        owner_user.refresh_from_db()
