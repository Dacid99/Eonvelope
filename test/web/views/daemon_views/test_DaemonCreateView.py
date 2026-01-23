# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import Daemon
from web.forms import CreateDaemonForm
from web.views import DaemonCreateView


@pytest.mark.django_db
def test_get__noauth(client, list_url, login_url):
    """Tests :class:`web.views.DaemonCreateView` with an unauthenticated user client."""
    response = client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(DaemonCreateView)}")


@pytest.mark.django_db
def test_get__auth_other(other_client, list_url):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated other user client."""
    response = other_client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
def test_get__auth_owner(owner_client, list_url):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    response = owner_client.get(list_url(DaemonCreateView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
def test_post__noauth(daemon_with_interval_payload, client, list_url, login_url):
    """Tests :class:`web.views.DaemonCreateView` with an unauthenticated user client."""
    assert Daemon.objects.all().count() == 1

    response = client.post(list_url(DaemonCreateView), daemon_with_interval_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={list_url(DaemonCreateView)}")
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post__auth_other(
    daemon_with_interval_payload, fake_other_mailbox, other_client, list_url
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
    assert (
        Daemon.objects.filter(
            fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
            mailbox=daemon_with_interval_payload["mailbox"],
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_post__auth__other__strange_mailbox(
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
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)


@pytest.mark.django_db
def test_post__auth_owner(daemon_with_interval_payload, owner_client, list_url):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + Daemon.get_list_web_url_name()))
    assert Daemon.objects.all().count() == 2
    assert (
        Daemon.objects.filter(
            fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
            mailbox=daemon_with_interval_payload["mailbox"],
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_post__duplicate__auth_owner(
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
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert response.context["form"].errors
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post__unavailable_criterion__auth_owner(
    fake_daemon, daemon_with_interval_payload, owner_client, list_url
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated owner user client."""
    fake_daemon.mailbox.account.protocol = EmailProtocolChoices.POP3
    fake_daemon.mailbox.account.save(update_fields=["protocol"])
    daemon_with_interval_payload["mailbox"] = fake_daemon.mailbox.id
    daemon_with_interval_payload["fetching_criterion"] = (
        EmailFetchingCriterionChoices.DRAFT
    )

    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert response.context["form"].errors
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post__auth_admin_strange_mailbox(
    daemon_with_interval_payload, admin_client, list_url
):
    """Tests :class:`web.views.DaemonCreateView` with the authenticated admin user client."""
    assert Daemon.objects.all().count() == 1

    response = admin_client.post(
        list_url(DaemonCreateView), daemon_with_interval_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert Daemon.objects.all().count() == 1
    assert "web/daemon/daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
