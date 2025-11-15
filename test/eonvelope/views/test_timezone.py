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

"""Test module for the :module:`eonvelope.views.timezone`."""

import pytest
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from eonvelope.middleware.TimezoneMiddleware import TimezoneMiddleware
from eonvelope.views.timezone import SET_TIMEZONE_URL_NAME
from test.web.conftest import other_client, owner_client


@pytest.mark.django_db
def test_get_noauth(client):
    """Tests `get` on :func:`eonvelope.views.timezone` for an unauthenticated user client."""
    response = client.get(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in client.session


@pytest.mark.django_db
def test_get_other(other_client):
    """Tests `get` on :func:`eonvelope.views.timezone` for the authenticated other user client."""
    response = other_client.get(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in other_client.session


@pytest.mark.django_db
def test_get_owner(owner_client):
    """Tests `get` on :func:`eonvelope.views.timezone` for the authenticated owner user client."""
    response = owner_client.get(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in owner_client.session


@pytest.mark.django_db
def test_post_noauth_good_timezone(client, fake_timezone):
    """Tests `post` on :func:`eonvelope.views.timezone` for an unauthenticated user client
    in case of an available timezone in the request.
    """
    response = client.post(reverse(SET_TIMEZONE_URL_NAME), {"timezone": fake_timezone})

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY in client.session
    assert client.session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] == fake_timezone


@pytest.mark.django_db
def test_post_noauth_no_timezone(client):
    """Tests `post` on :func:`eonvelope.views.timezone` for an unauthenticated user client
    in case of no timezone in the request.
    """
    response = client.post(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in client.session


@pytest.mark.django_db
def test_post_noauth_bad_timezone(client):
    """Tests `post` on :func:`eonvelope.views.timezone` for an unauthenticated user client
    in case of an unavailable timezone in the request.
    """
    response = client.post(reverse(SET_TIMEZONE_URL_NAME), {"timezone": "BAD/TZONE"})

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in client.session


@pytest.mark.django_db
def test_post_other_good_timezone(other_client, fake_timezone):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated other user client
    in case of an available timezone in the request.
    """
    response = other_client.post(
        reverse(SET_TIMEZONE_URL_NAME), {"timezone": fake_timezone}
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY in other_client.session
    assert (
        other_client.session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] == fake_timezone
    )


@pytest.mark.django_db
def test_post_other_no_timezone(other_client):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated other user client
    in case of no timezone in the request.
    """
    response = other_client.post(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in other_client.session


@pytest.mark.django_db
def test_post_other_bad_timezone(other_client):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated other user client
    in case of an unavailable timezone in the request.
    """
    response = other_client.post(
        reverse(SET_TIMEZONE_URL_NAME), {"timezone": "BAD/TZONE"}
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in other_client.session


@pytest.mark.django_db
def test_post_owner_good_timezone(owner_client, fake_timezone):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated owner user client
    in case of an available timezone in the request.
    """
    response = owner_client.post(
        reverse(SET_TIMEZONE_URL_NAME), {"timezone": fake_timezone}
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY in owner_client.session
    assert (
        owner_client.session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] == fake_timezone
    )


@pytest.mark.django_db
def test_post_owner_no_timezone(owner_client):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated owner user client
    in case of no timezone in the request.
    """
    response = owner_client.post(reverse(SET_TIMEZONE_URL_NAME))

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert response.url == "/"
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in owner_client.session


@pytest.mark.django_db
def test_post_owner_bad_timezone(owner_client):
    """Tests `post` on :func:`eonvelope.views.timezone` for the authenticated owner user client
    in case of an unavailable timezone in the request.
    """
    response = owner_client.post(
        reverse(SET_TIMEZONE_URL_NAME), {"timezone": "BAD/TZONE"}
    )

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == status.HTTP_302_FOUND
    assert TimezoneMiddleware.TIMEZONE_SESSION_KEY not in owner_client.session
