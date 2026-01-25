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

"""Test module for :mod:`web.views.MailboxUpdateOrDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Mailbox
from web.views import MailboxUpdateOrDeleteView


@pytest.mark.django_db
def test_get__noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxUpdateOrDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxUpdateOrDeleteView, fake_mailbox)}"
    )
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxUpdateOrDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxUpdateOrDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_edit.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "form" in response.context
    assert fake_mailbox.name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_admin(fake_mailbox, admin_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(MailboxUpdateOrDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_update__noauth(
    fake_mailbox, mailbox_payload, client, detail_url, login_url
):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox), mailbox_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxUpdateOrDeleteView, fake_mailbox)}"
    )
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]
    assert fake_mailbox.save_to_eml != mailbox_payload["save_to_eml"]


@pytest.mark.django_db
def test_post_update__auth_other(
    fake_mailbox, mailbox_payload, other_client, detail_url
):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox), mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]
    assert fake_mailbox.save_to_eml != mailbox_payload["save_to_eml"]


@pytest.mark.django_db
def test_post_update__auth_owner(
    fake_mailbox, mailbox_payload, owner_client, detail_url
):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox), mailbox_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:mailbox-filter-list"))
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments == mailbox_payload["save_attachments"]
    assert fake_mailbox.save_to_eml == mailbox_payload["save_to_eml"]


@pytest.mark.django_db
def test_post_update__auth_admin(
    fake_mailbox, mailbox_payload, admin_client, detail_url
):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox), mailbox_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailbox_payload["save_attachments"]
    assert fake_mailbox.save_to_eml != mailbox_payload["save_to_eml"]


@pytest.mark.django_db
def test_post_delete__noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxUpdateOrDeleteView, fake_mailbox)}"
    )
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_delete__auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_delete__auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:mailbox-filter-list"))
    with pytest.raises(Mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_post_delete__auth_admin(fake_mailbox, admin_client, detail_url):
    """Tests :class:`web.views.MailboxUpdateOrDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(MailboxUpdateOrDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None
