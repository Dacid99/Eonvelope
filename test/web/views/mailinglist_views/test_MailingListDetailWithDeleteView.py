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

"""Test module for :mod:`web.views.mailinglist_views.MailingListDetailWithDeleteView`."""

import pytest
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models.MailingListModel import MailingListModel
from web.views.mailinglist_views.MailingListDetailWithDeleteView import (
    MailingListDetailWithDeleteView,
)
from web.views.mailinglist_views.MailingListFilterView import MailingListFilterView


@pytest.mark.django_db
def test_get_noauth(mailingListModel, client, detail_url, login_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(MailingListDetailWithDeleteView, mailingListModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailingListDetailWithDeleteView, mailingListModel)}"
    )
    assert mailingListModel.list_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(mailingListModel, other_client, detail_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(MailingListDetailWithDeleteView, mailingListModel)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert mailingListModel.list_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(mailingListModel, owner_client, detail_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(MailingListDetailWithDeleteView, mailingListModel)
    )

    assert response.status_code == status.HTTP_200_OK
    assert mailingListModel.list_id in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(mailingListModel, client, detail_url, login_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailingListDetailWithDeleteView, mailingListModel)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailingListDetailWithDeleteView, mailingListModel)}"
    )
    mailingListModel.refresh_from_db()
    assert mailingListModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(mailingListModel, other_client, detail_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailingListDetailWithDeleteView, mailingListModel)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailingListModel.refresh_from_db()
    assert mailingListModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(mailingListModel, owner_client, detail_url):
    """Tests :class:`web.views.mailinglist_views.MailingListDetailWithDeleteView.MailingListDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailingListDetailWithDeleteView, mailingListModel)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + MailingListFilterView.URL_NAME))
    with pytest.raises(MailingListModel.DoesNotExist):
        mailingListModel.refresh_from_db()
