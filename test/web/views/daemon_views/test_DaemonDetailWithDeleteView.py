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

from core.models.Daemon import Daemon
from web.views.daemon_views.DaemonDetailWithDeleteView import DaemonDetailWithDeleteView
from web.views.daemon_views.DaemonFilterView import DaemonFilterView


@pytest.mark.django_db
def test_get_noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    assert fake_daemon.mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert fake_daemon.mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert fake_daemon.mailbox.name in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.daemon_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + DaemonFilterView.URL_NAME))
    with pytest.raises(Daemon.DoesNotExist):
        fake_daemon.refresh_from_db()


@pytest.mark.django_db
def test_post_start_noauth(
    fake_daemon,
    client,
    detail_url,
    login_url,
    mock_EmailArchiverDaemonRegistry_startDaemon,
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    mock_EmailArchiverDaemonRegistry_startDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_start_auth_other(
    fake_daemon, other_client, detail_url, mock_EmailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    mock_EmailArchiverDaemonRegistry_startDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_start_success_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "start_result" in response.context
    mock_EmailArchiverDaemonRegistry_startDaemon.assert_called_once_with(fake_daemon)


@pytest.mark.django_db
def test_post_start_failure_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EmailArchiverDaemonRegistry_startDaemon.return_value = False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": "Start"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "start_result" in response.context
    mock_EmailArchiverDaemonRegistry_startDaemon.assert_called_once_with(fake_daemon)


@pytest.mark.django_db
def test_post_start_missing_action_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_startDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EmailArchiverDaemonRegistry_startDaemon.return_value = False

    response = owner_client.post(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_EmailArchiverDaemonRegistry_startDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_stop_noauth(
    fake_daemon,
    client,
    detail_url,
    login_url,
    mock_EmailArchiverDaemonRegistry_stopDaemon,
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    mock_EmailArchiverDaemonRegistry_stopDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_stop_auth_other(
    fake_daemon, other_client, detail_url, mock_EmailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    mock_EmailArchiverDaemonRegistry_stopDaemon.assert_not_called()


@pytest.mark.django_db
def test_post_stop_success_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "stop_result" in response.context
    mock_EmailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(fake_daemon)


@pytest.mark.django_db
def test_post_stop_failure_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EmailArchiverDaemonRegistry_stopDaemon.return_value = False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": "Stop"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "stop_result" in response.context
    mock_EmailArchiverDaemonRegistry_stopDaemon.assert_called_once_with(fake_daemon)


@pytest.mark.django_db
def test_post_stop_missing_action_auth_owner(
    fake_daemon, owner_client, detail_url, mock_EmailArchiverDaemonRegistry_stopDaemon
):
    """Tests :class:`web.views.account_views.DaemonDetailWithDeleteView.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    mock_EmailArchiverDaemonRegistry_stopDaemon.return_value = False

    response = owner_client.post(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_EmailArchiverDaemonRegistry_stopDaemon.assert_not_called()
