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

"""Test module for :mod:`web.views.daemon_views.DaemonDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.DaemonModel import DaemonModel
from web.views.daemon_views.DaemonDetailWithDeleteView import DaemonDetailWithDeleteView
from web.views.daemon_views.DaemonFilterView import DaemonFilterView


@pytest.mark.django_db
def test_get_noauth(daemonModel, client, detail_url, login_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(DaemonDetailWithDeleteView, daemonModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, daemonModel)}"
    )
    assert daemonModel.mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(daemonModel, other_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(DaemonDetailWithDeleteView, daemonModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert daemonModel.mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(daemonModel, owner_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(DaemonDetailWithDeleteView, daemonModel))

    assert response.status_code == status.HTTP_200_OK
    assert daemonModel.mailbox.name in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(daemonModel, client, detail_url, login_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, daemonModel)}"
    )
    daemonModel.refresh_from_db()
    assert daemonModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(daemonModel, other_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    daemonModel.refresh_from_db()
    assert daemonModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(daemonModel, owner_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + DaemonFilterView.URL_NAME))
    with pytest.raises(DaemonModel.DoesNotExist):
        daemonModel.refresh_from_db()


@pytest.mark.django_db
def test_post_start_noauth(
    daemonModel,
    client,
    detail_url,
    login_url,
    mock_EMailArchiverDaemonRegistry_startDaemon,
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, daemonModel)}"
    )
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_start_auth_other(
    daemonModel, other_client, detail_url, mock_EMailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_start_success_auth_owner(
    daemonModel, owner_client, detail_url, mock_EMailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_called_once_with(daemonModel)

    assert "Daemon started successfully" in response.content.decode()


@pytest.mark.django_db
def test_post_start_failure_auth_owner(
    daemonModel, owner_client, detail_url, mock_EMailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EMailArchiverDaemonRegistry_startDaemon.return_value = False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_EMailArchiverDaemonRegistry_startDaemon.assert_called_once_with(daemonModel)
    assert "Daemon was already running" in response.content.decode()


@pytest.mark.django_db
def test_post_stop_noauth(
    daemonModel,
    client,
    detail_url,
    login_url,
    mock_EMailArchiverDaemonRegistry_stopDaemon,
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, daemonModel)}"
    )
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_stop_auth_other(
    daemonModel, other_client, detail_url, mock_EMailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_stop_success_auth_owner(
    daemonModel, owner_client, detail_url, mock_EMailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(daemonModel)
    assert "Daemon stopped successfully" in response.content.decode()


@pytest.mark.django_db
def test_post_stop_failure_auth_owner(
    daemonModel, owner_client, detail_url, mock_EMailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EMailArchiverDaemonRegistry_stopDaemon.return_value = False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, daemonModel),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_EMailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(daemonModel)
    assert "Daemon was not running" in response.content.decode()
