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

"""Test module for :mod:`web.views.EmailArchiveIndexView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from web.views import EmailArchiveIndexView


@pytest.mark.django_db
def test_get_noauth(client, login_url, date_url):
    """Tests :class:`web.views.EmailArchiveIndexView` with an unauthenticated user client."""
    response = client.get(date_url(EmailArchiveIndexView))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={date_url(EmailArchiveIndexView)}")


@pytest.mark.django_db
def test_get_auth_other(other_client, date_url):
    """Tests :class:`web.views.EmailArchiveIndexView` with the authenticated other user client."""
    response = other_client.get(date_url(EmailArchiveIndexView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/archive/index.html" in [
        template.name for template in response.templates
    ]
    assert "today" in response.context
    assert "page_obj" in response.context
    assert "page_size" in response.context
    assert "date_list" in response.context


@pytest.mark.django_db
def test_get_auth_owner(owner_client, date_url):
    """Tests :class:`web.views.EmailArchiveIndexView` with the authenticated owner user client."""
    response = owner_client.get(date_url(EmailArchiveIndexView))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/archive/index.html" in [
        template.name for template in response.templates
    ]
    assert "today" in response.context
    assert "page_obj" in response.context
    assert "page_size" in response.context
    assert "date_list" in response.context
