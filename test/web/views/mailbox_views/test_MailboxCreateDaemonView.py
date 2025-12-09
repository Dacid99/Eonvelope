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

"""Test module for :mod:`web.views.MailboxCreateDaemonView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import Daemon
from web.forms import CreateDaemonForm
from web.views import MailboxCreateDaemonView


@pytest.mark.django_db
def test_get_noauth(client, fake_mailbox, detail_url, login_url):
    """Tests :class:`web.views.MailboxCreateDaemonView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxCreateDaemonView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxCreateDaemonView, fake_mailbox)}"
    )


@pytest.mark.django_db
def test_get_auth_other(other_client, fake_mailbox, detail_url):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxCreateDaemonView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_owner(owner_client, fake_mailbox, detail_url):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxCreateDaemonView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
    assert response.context["form"].initial["mailbox"] == fake_mailbox.id
    assert "object" in response.context
    assert response.context["object"] == fake_mailbox


@pytest.mark.django_db
def test_get_auth_owner_criterion_choices(owner_client, fake_mailbox, detail_url):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated owner user client."""
    fake_mailbox.account.protocol = EmailProtocolChoices.POP3
    fake_mailbox.account.save(update_fields=["protocol"])

    response = owner_client.get(detail_url(MailboxCreateDaemonView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
    assert len(response.context["form"].fields["fetching_criterion"].choices) == 1
    assert response.context["form"].initial["mailbox"] == fake_mailbox.id
    assert "object" in response.context
    assert response.context["object"] == fake_mailbox


@pytest.mark.django_db
def test_get_auth_admin(admin_client, fake_mailbox, detail_url):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(MailboxCreateDaemonView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_noauth(
    daemon_with_interval_payload, client, fake_mailbox, detail_url, login_url
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with an unauthenticated user client."""
    assert Daemon.objects.all().count() == 1

    response = client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxCreateDaemonView, fake_mailbox)}"
    )
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post_auth_other(
    daemon_with_interval_payload,
    fake_other_mailbox,
    other_client,
    fake_mailbox,
    detail_url,
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated other user client."""
    daemon_with_interval_payload["mailbox"] = fake_other_mailbox.id

    assert Daemon.objects.all().count() == 1

    response = other_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_auth_owner(
    daemon_with_interval_payload, owner_client, fake_mailbox, detail_url
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated owner user client."""
    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )
    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(fake_mailbox.get_absolute_url())
    assert Daemon.objects.all().count() == 2
    assert (
        Daemon.objects.filter(
            fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
            mailbox=daemon_with_interval_payload["mailbox"],
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_post_auth_owner_other_mailbox(
    owner_client,
    fake_mailbox,
    fake_other_mailbox,
    daemon_with_interval_payload,
    detail_url,
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated other user client."""
    daemon_with_interval_payload["mailbox"] = fake_other_mailbox.id

    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert Daemon.objects.all().count() == 1
    assert "web/mailbox/mailbox_daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
    assert "mailbox" in response.context["form"].errors
    assert "object" in response.context
    assert response.context["object"] == fake_mailbox


@pytest.mark.django_db
def test_post_auth_owner_unavailable_criterion(
    owner_client,
    fake_mailbox,
    daemon_with_interval_payload,
    detail_url,
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated other user client."""
    fake_mailbox.account.protocol = EmailProtocolChoices.POP3
    fake_mailbox.account.save(update_fields=["protocol"])
    daemon_with_interval_payload["fetching_criterion"] = (
        EmailFetchingCriterionChoices.ANSWERED
    )

    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert Daemon.objects.all().count() == 1
    assert "web/mailbox/mailbox_daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
    assert "fetching_criterion" in response.context["form"].errors
    assert "object" in response.context
    assert response.context["object"] == fake_mailbox


@pytest.mark.django_db
def test_post_duplicate_auth_owner(
    fake_daemon, daemon_with_interval_payload, owner_client, fake_mailbox, detail_url
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated owner user client."""
    daemon_with_interval_payload["mailbox"] = fake_daemon.mailbox.id
    daemon_with_interval_payload["fetching_criterion"] = fake_daemon.fetching_criterion

    assert Daemon.objects.all().count() == 1

    response = owner_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_daemon_create.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert isinstance(response.context["form"], CreateDaemonForm)
    assert response.context["form"].errors
    assert "object" in response.context
    assert response.context["object"] == fake_mailbox
    assert Daemon.objects.all().count() == 1


@pytest.mark.django_db
def test_post_auth_admin(
    daemon_with_interval_payload,
    admin_client,
    fake_mailbox,
    detail_url,
):
    """Tests :class:`web.views.MailboxCreateDaemonView` with the authenticated admin user client."""
    assert Daemon.objects.all().count() == 1

    response = admin_client.post(
        detail_url(MailboxCreateDaemonView, fake_mailbox),
        daemon_with_interval_payload,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")
