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

"""Test module for :mod:`Emailkasten.Views.ImageViewSet`.

Fixtures:
    :func:`fixture_owner_user`: Creates a user that represents the owner of the data.
    :func:`fixture_other_user`: Creates a user that represents another user that is not the owner of the data.
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_imageModel`: Creates an email in `accountModel`.
    :func:`fixture_imageModel`: Creates an image in `emailModel`.
    :func:`fixture_emailPayload`: Creates clean :class:`Emailkasten.Models.ImageModel.ImageModel` payload for a post or put request.
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
from django.forms.models import model_to_dict
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status

from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.ImageModel import ImageModel
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Views.ImageViewSet import ImageViewSet

if TYPE_CHECKING:
    from typing import Any, Callable


@pytest.fixture(name='accountModel')
def fixture_accountModel(owner_user) -> AccountModel:
    """Creates an :class:`Emailkasten.Models.AccountModel.AccountModel`
    owned by :attr:`owner_user`.

    Args:
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel, user = owner_user)

@pytest.fixture(name='emailModel')
def fixture_emailModel(accountModel) -> EMailModel:
    """Creates an :class:`Emailkasten.Models.EMailModel.EMailModel`
    owned by :attr:`owner_user`.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(
        EMailModel,
        account=accountModel,
        eml_filepath=Faker().file_path(extension='eml'),
        prerender_filepath=Faker().file_path(extension='png')
    )


@pytest.fixture(name='imageModel')
def fixture_imageModel(emailModel) -> ImageModel:
    """Creates an :class:`Emailkasten.Models.ImageModel.ImageModel`
    owned by :attr:`owner_user`.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The image instance for testing.
    """
    return baker.make(
        ImageModel,
        email=emailModel,
        file_path=Faker().file_path(extension='pdf')
    )


@pytest.fixture(name='imagePayload')
def fixture_imagePayload(emailModel) -> dict[str, Any]:
    """Creates clean :class:`Emailkasten.Models.ImageModel.ImageModel` payload
    for a post or put request.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The clean payload.
    """
    imageData = baker.prepare(ImageModel, email=emailModel)
    payload = model_to_dict(imageData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload

@pytest.fixture(name='list_url')
def fixture_list_url() -> str:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return reverse(f'{ImageViewSet.BASENAME}-list')

@pytest.fixture(name='detail_url')
def fixture_detail_url(imageModel) -> str:
    """Gets the viewsets url for detail actions.

    Args:
        imageModel: Depends on :func:`fixture_imageModel`.

    Returns:
        The detail url."""
    return reverse(f'{ImageViewSet.BASENAME}-detail', args=[imageModel.id])

@pytest.fixture(name='custom_list_action_url')
def fixture_custom_list_action_url() -> Callable[[str],str]:
    """Gets the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda custom_list_action_url_name: (
        reverse(f'{ImageViewSet.BASENAME}-{custom_list_action_url_name}')
    )

@pytest.fixture(name='custom_detail_action_url')
def fixture_custom_detail_action_url(imageModel)-> Callable[[str],str]:
    """Gets the viewsets url for custom detail actions.

    Args:
        imageModel: Depends on :func:`fixture_imageModel`.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda custom_detail_action_url_name: (
        reverse(f'{ImageViewSet.BASENAME}-{custom_detail_action_url_name}', args=[imageModel.id])
    )


@pytest.mark.django_db
def test_list_noauth(imageModel, noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(imageModel, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_list_auth_owner(imageModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_noauth(imageModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']


@pytest.mark.django_db
def test_get_auth_other(imageModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['file_name']

@pytest.mark.django_db
def test_get_auth_owner(imageModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['file_name'] == imageModel.file_name


@pytest.mark.django_db
def test_patch_noauth(imageModel, noauth_apiClient, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(detail_url, data={'file_name': 'abc123'})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != 'abc123'


@pytest.mark.django_db
def test_patch_auth_other(imageModel, other_apiClient, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(detail_url, data={'file_name': 'abc123'})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != 'abc123'


@pytest.mark.django_db
def test_patch_auth_owner(imageModel, owner_apiClient, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(detail_url, data={'file_name': 'abc123'})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != 'abc123'


@pytest.mark.django_db
def test_put_noauth(imageModel, noauth_apiClient, imagePayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(detail_url, data=imagePayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != imagePayload['file_name']


@pytest.mark.django_db
def test_put_auth_other(imageModel, other_apiClient, imagePayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(detail_url, data=imagePayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != imagePayload['file_name']


@pytest.mark.django_db
def test_put_auth_owner(imageModel, owner_apiClient, imagePayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(detail_url, data=imagePayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    imageModel.refresh_from_db()
    assert imageModel.file_name != imagePayload['file_name']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, imagePayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url, data=imagePayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(ImageModel.DoesNotExist):
        ImageModel.objects.get(file_name = imagePayload['file_name'])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, imagePayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url, data=imagePayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(ImageModel.DoesNotExist):
        ImageModel.objects.get(file_name = imagePayload['file_name'])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, imagePayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url, data=imagePayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(ImageModel.DoesNotExist):
        ImageModel.objects.get(file_name = imagePayload['file_name'])


@pytest.mark.django_db
def test_delete_noauth(imageModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    imageModel.refresh_from_db()
    assert imageModel.file_name is not None


@pytest.mark.django_db
def test_delete_auth_other(imageModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    imageModel.refresh_from_db()
    assert imageModel.file_name is not None


@pytest.mark.django_db
def test_delete_auth_owner(imageModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    imageModel.refresh_from_db()
    assert imageModel.file_name is not None



@pytest.mark.django_db
def test_download_noauth(imageModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.download` action
    with an unauthenticated user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.ImageViewSet.open')

    response = noauth_apiClient.get(custom_detail_action_url(ImageViewSet.URL_NAME_DOWNLOAD))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(imageModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.download` action
    with the authenticated other user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.ImageViewSet.open')

    response = other_apiClient.get(custom_detail_action_url(ImageViewSet.URL_NAME_DOWNLOAD))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(imageModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.download` action
    with the authenticated owner user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.ImageViewSet.open')

    response = owner_apiClient.get(custom_detail_action_url(ImageViewSet.URL_NAME_DOWNLOAD))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()


@pytest.mark.django_db
def test_download_auth_owner(imageModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.download` action
    with the authenticated owner user client.
    """
    mockedFileContent = b'This is a 24 bytes file.'
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch('Emailkasten.Views.ImageViewSet.open', mock_open)
    mock_os_path_exists = mocker.patch('Emailkasten.Views.ImageViewSet.os.path.exists', return_value=True)

    response = owner_apiClient.get(custom_detail_action_url(ImageViewSet.URL_NAME_DOWNLOAD))

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once()
    mock_open.assert_called_once_with(imageModel.file_path, 'rb')
    assert 'Content-Disposition' in response.headers
    assert f'filename="{imageModel.file_name}"' in response['Content-Disposition']
    assert b''.join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_toggle_favorite_noauth(imageModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.toggle_favorite` action
    with an unauthenticated user client.
    """
    response = noauth_apiClient.post(custom_detail_action_url(ImageViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    imageModel.refresh_from_db()
    assert imageModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(imageModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.toggle_favorite` action
    with the authenticated other user client."""
    response = other_apiClient.post(custom_detail_action_url(ImageViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    imageModel.refresh_from_db()
    assert imageModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(imageModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.ImageViewSet.ImageViewSet.toggle_favorite` action
    with the authenticated owner user client."""
    response = owner_apiClient.post(custom_detail_action_url(ImageViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_200_OK
    imageModel.refresh_from_db()
    assert imageModel.is_favorite is True
