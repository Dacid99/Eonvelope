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

"""Test module for :mod:`web.views.correspondent_views.CorrespondentDetailWithDeleteView`."""

import pytest
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.CorrespondentModel import CorrespondentModel
from web.views.correspondent_views.CorrespondentDetailWithDeleteView import (
    CorrespondentDetailWithDeleteView,
)
from web.views.correspondent_views.CorrespondentFilterView import (
    CorrespondentFilterView,
)


@pytest.mark.django_db
def test_get_noauth(correspondentModel, client, detail_url, login_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentDetailWithDeleteView, correspondentModel)}"
    )
    assert correspondentModel.email_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(correspondentModel, other_client, detail_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert correspondentModel.email_address not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(correspondentModel, owner_client, detail_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_200_OK
    assert correspondentModel.email_address in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(correspondentModel, client, detail_url, login_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentDetailWithDeleteView, correspondentModel)}"
    )
    correspondentModel.refresh_from_db()
    assert correspondentModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(correspondentModel, other_client, detail_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    correspondentModel.refresh_from_db()
    assert correspondentModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(correspondentModel, owner_client, detail_url):
    """Tests :class:`web.views.correspondent_views.CorrespondentDetailWithDeleteView.CorrespondentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, correspondentModel)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + CorrespondentFilterView.URL_NAME))
    with pytest.raises(CorrespondentModel.DoesNotExist):
        correspondentModel.refresh_from_db()
