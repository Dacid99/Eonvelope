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

"""Test module for :mod:`web.views.CorrespondentEmailsTableView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from core.models import Correspondent
from web.views import CorrespondentEmailsTableView


@pytest.mark.django_db
def test_get_noauth(fake_correspondent, client, detail_url, login_url):
    """Tests :class:`web.views.CorrespondentEmailsTableView` with an unauthenticated user client."""
    response = client.get(detail_url(CorrespondentEmailsTableView, fake_correspondent))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentEmailsTableView, fake_correspondent)}"
    )


@pytest.mark.django_db
def test_get_auth_other(fake_correspondent, other_client, detail_url):
    """Tests :class:`web.views.CorrespondentEmailsTableView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(CorrespondentEmailsTableView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_correspondent.email_address not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_owner(fake_correspondent, owner_client, detail_url):
    """Tests :class:`web.views.CorrespondentEmailsTableView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(CorrespondentEmailsTableView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/correspondent/correspondent_email_table.html" in [
        template.name for template in response.templates
    ]
    assert "table" in response.context
    assert "page_obj" in response.context
    assert "page_size" in response.context
    assert "query" in response.context
    assert "correspondent" in response.context
    assert isinstance(response.context["correspondent"], Correspondent)

    with open("table.html", "w") as f:
        f.write(response.content.decode("utf-8"))
