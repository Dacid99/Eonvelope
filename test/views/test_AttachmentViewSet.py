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

"""Test module for :mod:`Emailkasten.Views.AttachmentViewSet`.

Fixtures:
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_emailModel`: Creates an email in `accountModel`.
    :func:`fixture_attachmentModel`: Creates an attachment in `emailModel`.
    :func:`fixture_emailPayload`: Creates clean :class:`Emailkasten.Models.AttachmentModel.AttachmentModel` payload for a patch, post or put request.
    :func:`fixture_list_url`: Gets the viewsets url for list actions.
    :func:`fixture_detail_url`: Gets the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Gets the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Gets the viewsets url for custom detail actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from faker import Faker
from model_bakery import baker
from rest_framework import status
from test_AccountViewSet import fixture_accountModel
from test_EMailViewSet import fixture_emailModel

from Emailkasten.Models.AttachmentModel import AttachmentModel
from Emailkasten.Views.AttachmentViewSet import AttachmentViewSet

if TYPE_CHECKING:
    from typing import Any, Callable


@pytest.fixture(name='attachmentModel')
def fixture_attachmentModel(emailModel) -> AttachmentModel:
    """Creates an :class:`Emailkasten.Models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(
        AttachmentModel,
        email=emailModel,
        file_path=Faker().file_path(extension='pdf')
    )


@pytest.fixture(name='attachmentPayload')
def fixture_attachmentPayload(emailModel) -> dict[str, Any]:
    """Creates clean :class:`Emailkasten.Models.AttachmentModel.AttachmentModel` payload for a patch, post or put request.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The clean payload.
    """
    attachmentData = baker.prepare(AttachmentModel, email=emailModel)
    payload = model_to_dict(attachmentData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload


@pytest.mark.django_db
def test_list_noauth(attachmentModel, noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(attachmentModel, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_list_auth_owner(attachmentModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(AttachmentViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_noauth(attachmentModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']


@pytest.mark.django_db
def test_get_auth_other(attachmentModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['file_name']

@pytest.mark.django_db
def test_get_auth_owner(attachmentModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['file_name'] == attachmentModel.file_name


@pytest.mark.django_db
def test_patch_noauth(attachmentModel, noauth_apiClient, attachmentPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_patch_auth_other(attachmentModel, other_apiClient, attachmentPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_patch_auth_owner(attachmentModel, owner_apiClient, attachmentPayload, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_put_noauth(attachmentModel, noauth_apiClient, attachmentPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_put_auth_other(attachmentModel, other_apiClient, attachmentPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_put_auth_owner(attachmentModel, owner_apiClient, attachmentPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(detail_url(AttachmentViewSet, attachmentModel), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name != attachmentPayload['file_name']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, attachmentPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(AttachmentViewSet), data=attachmentPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(AttachmentModel.DoesNotExist):
        AttachmentModel.objects.get(file_name = attachmentPayload['file_name'])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, attachmentPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(AttachmentViewSet), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(AttachmentModel.DoesNotExist):
        AttachmentModel.objects.get(file_name = attachmentPayload['file_name'])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, attachmentPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(AttachmentViewSet), data=attachmentPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['file_name']
    with pytest.raises(AttachmentModel.DoesNotExist):
        AttachmentModel.objects.get(file_name = attachmentPayload['file_name'])


@pytest.mark.django_db
def test_delete_noauth(attachmentModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name is not None


@pytest.mark.django_db
def test_delete_auth_other(attachmentModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name is not None


@pytest.mark.django_db
def test_delete_auth_owner(attachmentModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(AttachmentViewSet, attachmentModel))

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    attachmentModel.refresh_from_db()
    assert attachmentModel.file_name is not None



@pytest.mark.django_db
def test_download_noauth(attachmentModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.AttachmentViewSet.open')
    mock_os_path_exists = mocker.patch('Emailkasten.Views.AttachmentViewSet.os.path.exists', return_value=True)

    response = noauth_apiClient.get(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(attachmentModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.AttachmentViewSet.open')
    mock_os_path_exists = mocker.patch('Emailkasten.Views.AttachmentViewSet.os.path.exists', return_value=True)

    response = other_apiClient.get(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(attachmentModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    mock_open = mocker.patch('Emailkasten.Views.AttachmentViewSet.open')
    mock_os_path_exists = mocker.patch('Emailkasten.Views.AttachmentViewSet.os.path.exists', return_value=False)

    response = owner_apiClient.get(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once()


@pytest.mark.django_db
def test_download_auth_owner(attachmentModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the get method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    mockedFileContent = b'This is a 24 bytes file.'
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch('Emailkasten.Views.AttachmentViewSet.open', mock_open)
    mock_os_path_exists = mocker.patch('Emailkasten.Views.AttachmentViewSet.os.path.exists', return_value=True)

    response = owner_apiClient.get(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel))

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once()
    mock_open.assert_called_once_with(attachmentModel.file_path, 'rb')
    assert 'Content-Disposition' in response.headers
    assert f'filename="{attachmentModel.file_name}"' in response['Content-Disposition']
    assert b''.join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_toggle_favorite_noauth(attachmentModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with an unauthenticated user client.
    """
    response = noauth_apiClient.post(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE, attachmentModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(attachmentModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated other user client.
    """
    response = other_apiClient.post(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE, attachmentModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(attachmentModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated owner user client.
    """
    response = owner_apiClient.post(custom_detail_action_url(AttachmentViewSet, AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE, attachmentModel))

    assert response.status_code == status.HTTP_200_OK
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is True
