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

"""Test for the :module:`allauth` views and templates."""

import pytest
from django.http import HttpResponse
from django.urls import reverse
from rest_framework import status

from ...web.views.conftest import owner_client


@pytest.mark.django_db
def test_login(client):
    response = client.get(reverse("account_login"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_logout(owner_client):
    response = owner_client.get(reverse("account_logout"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_signup(client):
    response = client.get(reverse("account_signup"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_password(owner_client):
    response = owner_client.get(reverse("account_change_password"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_email(owner_client):
    response = owner_client.get(reverse("account_email"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_sessions(owner_client):
    response = owner_client.get(reverse("usersessions_list"))

    assert isinstance(response, HttpResponse)
    assert response.status_code == status.HTTP_200_OK
