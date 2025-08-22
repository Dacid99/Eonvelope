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
def mock_Daemon_test(mocker):
    return mocker.patch("api.v1.views.DaemonViewSet.Daemon.test", autospec=True)


@pytest.mark.django_db
def test_test_noauth(
    fake_daemon,
    noauth_api_client,
    custom_detail_action_url,
    mock_Daemon_test,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with an unauthenticated user client."""
    response = noauth_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "daemon" not in response.data
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_test_auth_other(
    fake_daemon,
    other_api_client,
    custom_detail_action_url,
    mock_Daemon_test,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated other user client."""
    response = other_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "daemon" not in response.data
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_test_success_auth_owner(
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
    mock_Daemon_test,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    assert response.data["result"] is True
    mock_Daemon_test.assert_called_once_with(fake_daemon)


@pytest.mark.django_db
def test_test_failure_auth_owner(
    faker,
    fake_daemon,
    owner_api_client,
    custom_detail_action_url,
    mock_Daemon_test,
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""
    mock_Daemon_test.side_effect = Exception(faker.sentence())

    response = owner_api_client.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, fake_daemon
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    assert response.data["result"] is False
    assert response.data["error"] == str(mock_Daemon_test.side_effect)
    mock_Daemon_test.assert_called_once_with(fake_daemon)


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
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
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
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
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
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
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
    fake_daemon.refresh_from_db()
    assert response.data["daemon"] == DaemonViewSet.serializer_class(fake_daemon).data
    assert fake_daemon.celery_task.enabled is False
