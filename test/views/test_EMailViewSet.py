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

"""Test module for :mod:`api.v1.views.EMailViewSet`.

Fixtures:
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_emailModel`: Creates an email in `accountModel`.
    :func:`fixture_emailPayload`: Creates clean :class:`core.models.EMailModel.EMailModel` payload for a patch, post or put request.

"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.EMailViewSet import EMailViewSet
from core.models.EMailModel import EMailModel

from .test_AccountViewSet import fixture_accountModel
from .test_MailboxViewSet import fixture_mailboxModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture(name="emailModel", autouse=True)
def fixture_emailModel(faker, mailboxModel) -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel` owned by :attr:`owner_user`.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(
        EMailModel,
        x_spam="NO",
        mailbox=mailboxModel,
        eml_filepath=faker.file_path(extension="eml"),
        prerender_filepath=faker.file_path(extension="png"),
    )


@pytest.fixture(name="emailPayload")
def fixture_emailPayload(mailboxModel) -> dict[str, Any]:
    """Creates clean :class:`core.models.EMailModel.EMailModel` payload for a patch, post or put request.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The clean payload.
    """
    emailData = baker.prepare(EMailModel, mailbox=mailboxModel)
    payload = model_to_dict(emailData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(EMailViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(emailModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]


@pytest.mark.django_db
def test_get_auth_other(emailModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["message_id"]


@pytest.mark.django_db
def test_get_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["message_id"] == emailModel.message_id


@pytest.mark.django_db
def test_patch_noauth(emailModel, noauth_apiClient, emailPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_patch_auth_other(emailModel, other_apiClient, emailPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_patch_auth_owner(emailModel, owner_apiClient, emailPayload, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_noauth(emailModel, noauth_apiClient, emailPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_auth_other(emailModel, other_apiClient, emailPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_put_auth_owner(emailModel, owner_apiClient, emailPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(EMailViewSet, emailModel), data=emailPayload
    )

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    emailModel.refresh_from_db()
    assert emailModel.message_id != emailPayload["message_id"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, emailPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, emailPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, emailPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(EMailViewSet), data=emailPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["message_id"]
    with pytest.raises(EMailModel.DoesNotExist):
        EMailModel.objects.get(message_id=emailPayload["message_id"])


@pytest.mark.django_db
def test_delete_noauth(emailModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None


@pytest.mark.django_db
def test_delete_auth_other(emailModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None


@pytest.mark.django_db
def test_delete_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(EMailModel.DoesNotExist):
        emailModel.refresh_from_db()


@pytest.mark.django_db
def test_delete_nonexistant_auth_owner(emailModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    old_id = emailModel.id
    emailModel.id = 10
    response = owner_apiClient.delete(detail_url(EMailViewSet, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.id = old_id
    emailModel.refresh_from_db()
    assert emailModel.message_id is not None


@pytest.mark.django_db
def test_download_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=False
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=False
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=False
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(emailModel.eml_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.EMailViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=True
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(emailModel.eml_filepath)
    mock_open.assert_called_once_with(emailModel.eml_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(emailModel.eml_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_prerender_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with an unauthenticated user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=True
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_prerender_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated other user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=True
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_prerender_no_file_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated owner user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=False
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(emailModel.prerender_filepath)


@pytest.mark.django_db
def test_prerender_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.EMailViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", return_value=True
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(emailModel.prerender_filepath)
    mock_open.assert_called_once_with(emailModel.prerender_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(emailModel.prerender_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_subConversation_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation"
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_subConversation.assert_not_called()


@pytest.mark.django_db
def test_subConversation_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation"
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_subConversation.assert_not_called()


@pytest.mark.django_db
def test_subConversation_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation",
        return_value=[emailModel],
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == emailModel.id
    mock_subConversation.assert_called_once_with()


@pytest.mark.django_db
def test_fullConversation_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation"
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_fullConversation.assert_not_called()


@pytest.mark.django_db
def test_fullConversation_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation"
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_fullConversation.assert_not_called()


@pytest.mark.django_db
def test_fullConversation_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation",
        return_value=[emailModel],
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == emailModel.id
    mock_fullConversation.assert_called_once_with()


@pytest.mark.django_db
def test_toggle_favorite_noauth(emailModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is True
