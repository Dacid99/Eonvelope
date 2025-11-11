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

"""Test module for the :module:`eonvelope.views.UserProfileView`."""

import pytest
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from eonvelope.models import UserProfile
from eonvelope.views import UserProfileView
from test.web.conftest import other_client, owner_client


@pytest.mark.django_db
def test_get_noauth(client, login_url):
    """Tests `get` on :class:`eonvelope.views.UserProfileView` for an unauthenticated user client."""
    response = client.get(reverse(UserProfileView.URL_NAME))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={reverse(UserProfileView.URL_NAME)}")


@pytest.mark.django_db
def test_get_auth_other(other_user, other_client):
    """Tests :class:`eonvelope.views.UserProfileView` with the authenticated owner user client."""
    response = other_client.get(reverse(UserProfileView.URL_NAME))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "account/profile.html" in [template.name for template in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], UserProfile)
    assert response.context["object"] == other_user.profile
    assert "form" in response.context


@pytest.mark.django_db
def test_get_auth_owner(owner_user, owner_client):
    """Tests :class:`eonvelope.views.UserProfileView` with the authenticated owner user client."""
    response = owner_client.get(reverse(UserProfileView.URL_NAME))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "account/profile.html" in [template.name for template in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], UserProfile)
    assert response.context["object"] == owner_user.profile
    assert "form" in response.context


@pytest.mark.django_db
def test_post_update_noauth(profile_payload, client, login_url):
    """Tests :class:`eonvelope.views.UserProfileView` with an unauthenticated user client."""
    response = client.post(reverse(UserProfileView.URL_NAME), profile_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={reverse(UserProfileView.URL_NAME)}")


@pytest.mark.django_db
def test_post_update_auth_other(other_user, profile_payload, other_client):
    """Tests :class:`eonvelope.views.UserProfileView` with the authenticated other user client."""
    response = other_client.post(reverse(UserProfileView.URL_NAME), profile_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse(UserProfileView.URL_NAME))
    other_user.refresh_from_db()
    assert other_user.profile.paperless_url == profile_payload["paperless_url"]
    assert other_user.profile.paperless_api_key == profile_payload["paperless_api_key"]
    assert (
        other_user.profile.paperless_tika_enabled
        == profile_payload["paperless_tika_enabled"]
    )


@pytest.mark.django_db
def test_post_update_auth_owner(owner_user, profile_payload, owner_client):
    """Tests :class:`eonvelope.views.UserProfileView` with the authenticated owner user client."""
    response = owner_client.post(reverse(UserProfileView.URL_NAME), profile_payload)

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse(UserProfileView.URL_NAME))
    owner_user.refresh_from_db()
    assert owner_user.profile.paperless_url == profile_payload["paperless_url"]
    assert owner_user.profile.paperless_api_key == profile_payload["paperless_api_key"]
    assert (
        owner_user.profile.paperless_tika_enabled
        == profile_payload["paperless_tika_enabled"]
    )
