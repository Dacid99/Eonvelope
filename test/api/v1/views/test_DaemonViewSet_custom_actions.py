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

from api.v1.views import DaemonViewSet


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
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
def mock_Mailbox_get_available_fetching_criteria(mocker, faker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Mailbox.get_available_fetching_criteria",
        autospec=True,
        return_value=faker.words(),
    )


@pytest.mark.django_db
def test_fetching_options_noauth(
    noauth_api_client,
    custom_detail_action_url,
    fake_daemon,
    mock_Mailbox_get_available_fetching_criteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_get_available_fetching_criteria.assert_not_called()


@pytest.mark.django_db
def test_fetching_options_auth_other(
    other_api_client,
    custom_detail_action_url,
    fake_daemon,
    mock_Mailbox_get_available_fetching_criteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_get_available_fetching_criteria.assert_not_called()


@pytest.mark.django_db
def test_fetching_options_auth_owner(
    owner_api_client,
    custom_detail_action_url,
    fake_daemon,
    mock_Mailbox_get_available_fetching_criteria,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["options"]
        == mock_Mailbox_get_available_fetching_criteria.return_value
    )
    mock_Mailbox_get_available_fetching_criteria.assert_called_once_with(
        fake_daemon.mailbox
    )


@pytest.mark.django_db
def test_start_noauth(
    fake_daemon,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with an unauthenticated user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = noauth_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False
    assert "daemon" not in response.data


@pytest.mark.django_db
def test_start_auth_other(
    fake_daemon,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated other user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = other_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False
    assert "daemon" not in response.data


@pytest.mark.django_db
def test_start_success_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_start_failure_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""
    assert fake_daemon.celery_task.enabled is True

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_stop_noauth(
    fake_daemon,
    noauth_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with an unauthenticated user client."""
    assert fake_daemon.celery_task.enabled is True

    response = noauth_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True
    assert "daemon" not in response.data


@pytest.mark.django_db
def test_stop_auth_other(
    fake_daemon,
    other_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated other user client."""
    assert fake_daemon.celery_task.enabled is True

    response = other_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True
    assert "daemon" not in response.data


@pytest.mark.django_db
def test_stop_success_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    assert fake_daemon.celery_task.enabled is True

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_stop_failure_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_download_noauth(
    fake_daemon,
    noauth_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with an unauthenticated user client."""
    response = noauth_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    fake_daemon,
    other_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated other user client."""
    response = other_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    mock_os_path_exists.return_value = False
    mock_open.side_effect = FileNotFoundError

    response = owner_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(fake_daemon.log_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    response = owner_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(fake_daemon.log_filepath)
    mock_open.assert_called_once_with(fake_daemon.log_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(fake_daemon.log_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mock_open().read()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "number_query_param, expected_suffix", [("1", ".1"), ("0", ""), ("abc", "")]
)
def test_download_auth_owner_numberquery(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
    mock_open,
    mock_os_path_exists,
    number_query_param,
    expected_suffix,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    expected_log_filepath = fake_daemon.log_filepath + expected_suffix

    response = owner_api_client.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, fake_daemon
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
