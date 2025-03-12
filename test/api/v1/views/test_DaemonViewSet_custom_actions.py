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

import os

import pytest
from rest_framework import status

from api.v1.views.DaemonViewSet import DaemonViewSet


@pytest.fixture
def mock_open(mocker, faker):
    fake_content = faker.text().encode("utf-8")
    mock_open = mocker.mock_open(read_data=fake_content)
    mocker.patch("api.v1.views.DaemonViewSet.open", mock_open)
    return mock_open


@pytest.fixture
def mock_os_path_exists(mocker):
    return mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_MailboxModel_getAvailableFetchingCriteria(mocker, faker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.MailboxModel.getAvailableFetchingCriteria",
        autospec=True,
        return_value=faker.words(),
    )


@pytest.fixture
def mock_EMailArchiverDaemonRegistry_testDaemon(mocker):
    return mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.testDaemon",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_EMailArchiverDaemonRegistry_startDaemon(mocker):
    return mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.startDaemon",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_EMailArchiverDaemonRegistry_stopDaemon(mocker):
    return mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.stopDaemon",
        autospec=True,
        return_value=True,
    )


@pytest.mark.django_db
def test_fetching_options_noauth(
    noauth_apiClient,
    custom_detail_action_url,
    daemonModel,
    mock_MailboxModel_getAvailableFetchingCriteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with an unauthenticated user client."""
    response = noauth_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_MailboxModel_getAvailableFetchingCriteria.assert_not_called()


@pytest.mark.django_db
def test_fetching_options_auth_other(
    other_apiClient,
    custom_detail_action_url,
    daemonModel,
    mock_MailboxModel_getAvailableFetchingCriteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated other user client."""
    response = other_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_getAvailableFetchingCriteria.assert_not_called()


@pytest.mark.django_db
def test_fetching_options_auth_owner(
    owner_apiClient,
    custom_detail_action_url,
    daemonModel,
    mock_MailboxModel_getAvailableFetchingCriteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated owner user client."""
    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["options"]
        == mock_MailboxModel_getAvailableFetchingCriteria.return_value
    )
    mock_MailboxModel_getAvailableFetchingCriteria.assert_called_once_with(
        daemonModel.mailbox
    )


@pytest.mark.django_db
def test_test_noauth(
    daemonModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_testDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["daemon"]
    mock_EMailArchiverDaemonRegistry_testDaemon.assert_not_called()


@pytest.mark.django_db
def test_test_auth_other(
    daemonModel,
    other_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_testDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["daemon"]
    mock_EMailArchiverDaemonRegistry_testDaemon.assert_not_called()


@pytest.mark.django_db
def test_test_success_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_testDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    assert response.data["result"] is True
    mock_EMailArchiverDaemonRegistry_testDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_test_failure_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_testDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""
    mock_EMailArchiverDaemonRegistry_testDaemon.return_value = False

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    assert response.data["result"] is False
    mock_EMailArchiverDaemonRegistry_testDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_start_noauth(
    daemonModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_startDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with an unauthenticated user client."""

    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_start_auth_other(
    daemonModel,
    other_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_startDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_start_success_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_startDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_start_failure_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_startDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""
    mock_EMailArchiverDaemonRegistry_startDaemon.return_value = False

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_stop_noauth(
    daemonModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_stopDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_stop_auth_other(
    daemonModel,
    other_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_stopDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_stop_success_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_stopDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_stop_failure_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailArchiverDaemonRegistry_stopDaemon,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    mock_EMailArchiverDaemonRegistry_stopDaemon.return_value = False

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_download_noauth(
    daemonModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with an unauthenticated user client."""
    response = noauth_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    daemonModel,
    other_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated other user client."""
    response = other_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    mock_os_path_exists.return_value = False
    mock_open.side_effect = FileNotFoundError

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(daemonModel.log_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(daemonModel.log_filepath)
    mock_open.assert_called_once_with(daemonModel.log_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(daemonModel.log_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "number_query_param, expected_suffix", [("1", ".1"), ("0", ""), ("abc", "")]
)
def test_download_auth_owner_numberquery(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
    number_query_param,
    expected_suffix,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    expected_log_filepath = daemonModel.log_filepath + expected_suffix

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        ),
        {"number": number_query_param},
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(expected_log_filepath)
    mock_open.assert_called_once_with(expected_log_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(expected_log_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mock_open().read()
