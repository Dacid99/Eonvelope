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

"""Test module for :mod:`web.views.MailboxEmailsTableView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from web.views import MailboxEmailsTableView


@pytest.mark.django_db
def test_get_noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxEmailsTableView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxEmailsTableView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxEmailsTableView, fake_mailbox)}"
    )


@pytest.mark.django_db
def test_get_auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxEmailsTableView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxEmailsTableView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxEmailsTableView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxEmailsTableView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_email_table.html" in [
        template.name for template in response.templates
    ]
    assert "table" in response.context
    assert "page_obj" in response.context
    assert "page_size" in response.context
    assert "query" in response.context
    assert "mailbox" in response.context
