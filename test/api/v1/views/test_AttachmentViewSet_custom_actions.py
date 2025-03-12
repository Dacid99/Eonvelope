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

"""Test module for :mod:`api.v1.views.AttachmentViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.AttachmentViewSet import AttachmentViewSet


@pytest.fixture(name="mock_open")
def fixture_mock_open(mocker, faker):
    fake_content = faker.text().encode("utf-8")
    mock_open = mocker.mock_open(read_data=fake_content)
    mocker.patch("api.v1.views.AttachmentViewSet.open", mock_open)
    return mock_open


@pytest.fixture(name="mock_os_path_exists")
def fixture_mock_os_path_exists(mocker):
    return mocker.patch(
        "api.v1.views.AttachmentViewSet.os.path.exists",
        autospec=True,
        return_value=True,
    )


@pytest.mark.django_db
def test_download_noauth(
    attachmentModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with an unauthenticated user client.
    """
    response = noauth_apiClient.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    attachmentModel,
    other_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated other user client.
    """
    response = other_apiClient.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    attachmentModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    mock_open.side_effect = FileNotFoundError
    mock_os_path_exists.return_value = False

    response = owner_apiClient.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(attachmentModel.file_path)


@pytest.mark.django_db
def test_download_auth_owner(
    attachmentModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.download` action
    with the authenticated owner user client.
    """
    response = owner_apiClient.get(
        custom_detail_action_url(
            AttachmentViewSet, AttachmentViewSet.URL_NAME_DOWNLOAD, attachmentModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(attachmentModel.file_path)
    mock_open.assert_called_once_with(attachmentModel.file_path, "rb")
    assert "Content-Disposition" in response.headers
    assert f'filename="{attachmentModel.file_name}"' in response["Content-Disposition"]
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    attachmentModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with an unauthenticated user client.
    """
    response = noauth_apiClient.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            attachmentModel,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    attachmentModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated other user client.
    """
    response = other_apiClient.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            attachmentModel,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    attachmentModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.AttachmentViewSet.AttachmentViewSet.toggle_favorite` action
    with the authenticated owner user client.
    """
    response = owner_apiClient.post(
        custom_detail_action_url(
            AttachmentViewSet,
            AttachmentViewSet.URL_NAME_TOGGLE_FAVORITE,
            attachmentModel,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    attachmentModel.refresh_from_db()
    assert attachmentModel.is_favorite is True
