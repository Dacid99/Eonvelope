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

"""Test module for :mod:`web.views.DaemonCreateView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Daemon
from web.forms import CreateDaemonForm
from web.views import DaemonCreateView


@pytest.mark.django_db
def test_get_noauth(client, list_url, login_url):
    """Tests :class:`web.views.DaemonCreateView` with an unauthenticated user client."""
    response = client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(DaemonCreateView)}")


@pytest.mark.django_db
def test_get_auth_other(other_client, list_url):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated other user client."""
    response = other_client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
def test_get_auth_owner(owner_client, list_url):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    response = owner_client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
def test_post_noauth(daemon_with_interval_payload, client, list_url, login_url):
    """Tests :class:`web.views.DaemonCreateView` with an unauthenticated user client."""
    assert Daemon.objects.all().count() == 1

    response = client.post(list_url(DaemonCreateView), daemon_with_interval_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(DaemonCreateView)}")
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post_auth_other(
    fake_fs, daemon_with_interval_payload, fake_other_mailbox, other_client, list_url
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated other user client."""
    daemon_with_interval_payload["mailbox"] = fake_other_mailbox.id

    assert Daemon.objects.all().count() == 1

    response = other_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Daemon.get_list_web_url_name()))
    assert Daemon.objects.all().count() == 2
    added_daemon = Daemon.objects.filter(
        fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
        mailbox=daemon_with_interval_payload["mailbox"],
    ).get()
    assert (
        added_daemon.log_backup_count
        == daemon_with_interval_payload["log_backup_count"]
    )
    assert added_daemon.logfile_size == daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_auth_other_strange_mailbox(
    daemon_with_interval_payload, other_client, list_url
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated other user client."""
    assert Daemon.objects.all().count() == 1

    response = other_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert Daemon.objects.all().count() == 1
    assert "web/daemon/daemon_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
@pytest.mark.parametrize("run", range(100))
def test_post_auth_owner(
    fake_fs, daemon_with_interval_payload, owner_client, list_url, run
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Daemon.get_list_web_url_name()))
    assert Daemon.objects.all().count() == 2
    added_daemon = Daemon.objects.filter(
        fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
        mailbox=daemon_with_interval_payload["mailbox"],
    ).get()
    assert (
        added_daemon.log_backup_count
        == daemon_with_interval_payload["log_backup_count"]
    )
    assert added_daemon.logfile_size == daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_duplicate_auth_owner(
    fake_daemon, daemon_with_interval_payload, owner_client, list_url
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    daemon_with_interval_payload["mailbox"] = fake_daemon.mailbox.id
    daemon_with_interval_payload["fetching_criterion"] = fake_daemon.fetching_criterion

    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert Daemon.objects.all().count() == 1
