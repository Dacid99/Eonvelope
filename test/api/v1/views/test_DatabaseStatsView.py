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

"""Test module for :mod:`api.v1.views.DatabaseStatsView`."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.DatabaseStatsView import DatabaseStatsView


@pytest.mark.django_db
def test_list__noauth(noauth_api_client, url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_api_client.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_count" not in response.data


@pytest.mark.django_db
def test_list__auth_other(fake_email, other_api_client, url):
    """Tests the list method with the authenticated other user client."""
    response = other_api_client.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_count"] == 0
    assert response.data["correspondent_count"] == 0
    assert response.data["attachment_count"] == 0
    assert response.data["account_count"] == 0
    assert response.data["mailbox_count"] == 0
    assert response.data["daemon_count"] == 0


@pytest.mark.django_db
def test_list__auth_owner(fake_email, owner_api_client, url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_api_client.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_count"] == 1
    assert response.data["correspondent_count"] == 1
    assert response.data["attachment_count"] == 1
    assert response.data["account_count"] == 1
    assert response.data["mailbox_count"] == 1
    assert response.data["daemon_count"] == 1


@pytest.mark.django_db
def test_list__auth_admin(fake_email, admin_api_client, url):
    """Tests the list method with the authenticated admin user client."""
    response = admin_api_client.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_count"] == 0
    assert response.data["correspondent_count"] == 0
    assert response.data["attachment_count"] == 0
    assert response.data["account_count"] == 0
    assert response.data["mailbox_count"] == 0
    assert response.data["daemon_count"] == 0


@pytest.mark.django_db
def test_post__noauth(noauth_api_client, url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_api_client.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "email_count" not in response.data


@pytest.mark.django_db
def test_post__auth_other(other_api_client, url):
    """Tests the post method with the authenticated other user client."""
    response = other_api_client.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_count" not in response.data


@pytest.mark.django_db
def test_post__auth_owner(owner_api_client, url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_api_client.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_count" not in response.data


@pytest.mark.django_db
def test_post__auth_admin(admin_api_client, url):
    """Tests the post method with the authenticated admin user client."""
    response = admin_api_client.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "email_count" not in response.data
