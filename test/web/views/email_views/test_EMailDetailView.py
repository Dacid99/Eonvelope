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

"""Test module for :mod:`web.views.email_views.EMailDetailView`."""

import pytest
from django.http import HttpResponseRedirect
from rest_framework import status

from web.views.email_views.EMailDetailView import EMailDetailView


@pytest.mark.django_db
def test_view_noauth(emailModel, client, detail_url, login_url):
    """Tests :class:`web.views.email_views.EMailDetailView.EMailDetailView` with an unauthenticated user client."""
    response = client.get(detail_url(EMailDetailView, emailModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={detail_url(EMailDetailView, emailModel)}")
    assert emailModel.message_id not in response.content.decode()


@pytest.mark.django_db
def test_view_auth_other(emailModel, other_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailView.EMailDetailView` with the authenticated other user client."""
    response = other_client.get(detail_url(EMailDetailView, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert emailModel.message_id not in response.content.decode()


@pytest.mark.django_db
def test_view_auth_owner(emailModel, owner_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailView.EMailDetailView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(EMailDetailView, emailModel))

    assert response.status_code == status.HTTP_200_OK
    assert emailModel.message_id in response.content.decode()
