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

"""Test module for :mod:`web.views.email_views.EMailDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.EMailModel import EMailModel
from web.views.email_views.EMailDetailWithDeleteView import EMailDetailWithDeleteView
from web.views.email_views.EMailFilterView import EMailFilterView


@pytest.mark.django_db
def test_get_noauth(emailModel, client, detail_url, login_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EMailDetailWithDeleteView, emailModel)}"
    )
    assert emailModel.message_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(emailModel, other_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert emailModel.message_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(emailModel, owner_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], EMailModel)
    assert emailModel.message_id in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(emailModel, client, detail_url, login_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EMailDetailWithDeleteView, emailModel)}"
    )
    emailModel.refresh_from_db()
    assert emailModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(emailModel, other_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    emailModel.refresh_from_db()
    assert emailModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(emailModel, owner_client, detail_url):
    """Tests :class:`web.views.email_views.EMailDetailWithDeleteView.EMailDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(detail_url(EMailDetailWithDeleteView, emailModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + EMailFilterView.URL_NAME))
    with pytest.raises(EMailModel.DoesNotExist):
        emailModel.refresh_from_db()
