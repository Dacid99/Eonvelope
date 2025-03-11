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

"""Test module for :mod:`api.v1.views.DatabaseStatsView`."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse
from rest_framework import status

from api.v1.views.DatabaseStatsView import DatabaseStatsView


if TYPE_CHECKING:
    from collections.abc import Callable

    from rest_framework.viewsets import ModelViewSet


@pytest.fixture(name="url")
def fixture_url() -> Callable[[type[ModelViewSet]], str]:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda viewClass: reverse(f"{viewClass.NAME}")


@pytest.mark.django_db
def test_list_noauth(noauth_apiClient, url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_count"]


@pytest.mark.django_db
def test_list_auth_other(other_apiClient, url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_count"] == 0
    assert response.data["correspondent_count"] == 0
    assert response.data["attachment_count"] == 0
    assert response.data["account_count"] == 0


@pytest.mark.django_db
def test_list_auth_owner(owner_apiClient, url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(url(DatabaseStatsView))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["email_count"] == 1
    assert response.data["correspondent_count"] == 1
    assert response.data["attachment_count"] == 1
    assert response.data["account_count"] == 1


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["email_count"]


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_count"]


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(url(DatabaseStatsView), data={})

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["email_count"]
