# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Test module for the Emailkasten urls in :mod:`Emailkasten.urls`."""

import pytest
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status

from test.web.conftest import owner_client


@pytest.mark.django_db
def test_login(client):
    """Tests allauths login."""
    response = client.get(reverse("account_login"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logout(owner_client):
    """Tests allauths logout."""
    response = owner_client.get(reverse("account_logout"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_signup(client):
    """Tests allauths signup."""
    response = client.get(reverse("account_signup"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_password(owner_client):
    """Tests allauths change password."""
    response = owner_client.get(reverse("account_change_password"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_email(owner_client):
    """Tests allauths email view."""
    response = owner_client.get(reverse("account_email"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sessions(owner_client):
    """Tests allauths sessions view."""
    response = owner_client.get(reverse("usersessions_list"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK
