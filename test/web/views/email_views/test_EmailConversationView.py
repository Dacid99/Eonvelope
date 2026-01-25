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

"""Test module for :mod:`web.views.EmailConversationView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from core.models import Email
from web.views import EmailConversationView


@pytest.mark.django_db
def test_get__noauth(fake_email, client, detail_url, login_url):
    """Tests :class:`web.views.EmailConversationView` with an unauthenticated user client."""
    response = client.get(detail_url(EmailConversationView, fake_email))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EmailConversationView, fake_email)}"
    )


@pytest.mark.django_db
def test_get__auth_other(fake_email, other_client, detail_url):
    """Tests :class:`web.views.EmailConversationView` with the authenticated other user client."""
    response = other_client.get(detail_url(EmailConversationView, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_email.message_id not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_owner(fake_email, fake_email_conversation, owner_client, detail_url):
    """Tests :class:`web.views.EmailConversationView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(EmailConversationView, fake_email))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_conversation_filter_list.html" in [
        template.name for template in response.templates
    ]
    assert "page_obj" in response.context
    assert response.context["page_obj"].object_list
    assert isinstance(response.context["page_obj"].object_list[0], Email)
    assert "page_size" in response.context
    assert "query" in response.context
    assert "email" in response.context
    assert all(
        context_email in fake_email.conversation.all()
        for context_email in response.context["page_obj"]
    )
    assert len(fake_email.conversation.all()) == len(response.context["page_obj"])


@pytest.mark.django_db
def test_get__auth_admin(fake_email, admin_client, detail_url):
    """Tests :class:`web.views.EmailConversationView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(EmailConversationView, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_email.message_id not in response.content.decode("utf-8")
