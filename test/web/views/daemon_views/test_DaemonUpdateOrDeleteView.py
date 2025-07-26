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

"""Test module for :mod:`web.views.DaemonUpdateOrDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Daemon
from web.views import DaemonUpdateOrDeleteView


@pytest.mark.django_db
def test_get_noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(DaemonUpdateOrDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonUpdateOrDeleteView, fake_daemon)}"
    )
    assert str(fake_daemon.uuid) not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(DaemonUpdateOrDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert str(fake_daemon.uuid) not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(DaemonUpdateOrDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_edit.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "form" in response.context
    assert str(fake_daemon.uuid) in response.content.decode()


@pytest.mark.django_db
def test_post_update_noauth(
    fake_daemon, daemon_with_interval_payload, client, detail_url, login_url
):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonUpdateOrDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert (
        fake_daemon.log_backup_count != daemon_with_interval_payload["log_backup_count"]
    )
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_update_auth_other(
    fake_daemon, daemon_with_interval_payload, other_client, detail_url
):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    fake_daemon.refresh_from_db()
    assert (
        fake_daemon.log_backup_count != daemon_with_interval_payload["log_backup_count"]
    )
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_update_auth_owner(
    fake_daemon, daemon_with_interval_payload, owner_client, detail_url
):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:daemon-filter-list"))
    fake_daemon.refresh_from_db()
    assert (
        fake_daemon.log_backup_count == daemon_with_interval_payload["log_backup_count"]
    )
    assert fake_daemon.logfile_size == daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_delete_noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonUpdateOrDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonUpdateOrDeleteView, fake_daemon),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:daemon-filter-list"))
    with pytest.raises(Daemon.DoesNotExist):
        fake_daemon.refresh_from_db()
