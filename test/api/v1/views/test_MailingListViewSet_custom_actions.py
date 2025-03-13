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

"""Test module for :mod:`api.v1.views.MailingListViewSet`'s custom actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.MailingListViewSet import MailingListViewSet


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    mailingListModel, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailingListViewSet.MailingListViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailingListViewSet,
            MailingListViewSet.URL_NAME_TOGGLE_FAVORITE,
            mailingListModel,
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailingListModel.refresh_from_db()
    assert mailingListModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    mailingListModel, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailingListViewSet.MailingListViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            MailingListViewSet,
            MailingListViewSet.URL_NAME_TOGGLE_FAVORITE,
            mailingListModel,
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailingListModel.refresh_from_db()
    assert mailingListModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    mailingListModel, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailingListViewSet.MailingListViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailingListViewSet,
            MailingListViewSet.URL_NAME_TOGGLE_FAVORITE,
            mailingListModel,
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mailingListModel.refresh_from_db()
    assert mailingListModel.is_favorite is True
