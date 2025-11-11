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

"""Test module for the api root urls in :mod:`api.urls`."""

import pytest
from django.http import HttpResponsePermanentRedirect
from rest_framework import status


@pytest.mark.django_db
def test_dashboard_redirect(owner_api_client):
    """Tests the permanent redirect from api root to v1."""
    response = owner_api_client.get("/api/")
    assert response.status_code == status.HTTP_301_MOVED_PERMANENTLY
    assert isinstance(response, HttpResponsePermanentRedirect)
    assert response.url == "v1/"
