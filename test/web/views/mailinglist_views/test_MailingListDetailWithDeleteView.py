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

"""Test module for :mod:`web.views.MailingListDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import MailingList
from web.views import MailingListFilterView
from web.views.mailinglist_views.MailingListDetailWithDeleteView import (
    MailingListDetailWithDeleteView,
)


@pytest.mark.django_db
def test_get_noauth(fake_mailing_list, client, detail_url, login_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailingListDetailWithDeleteView, fake_mailing_list)}"
    )
    assert fake_mailing_list.list_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_mailing_list, other_client, detail_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert fake_mailing_list.list_id not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_mailing_list, owner_client, detail_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailinglist/mailinglist_detail.html" in [
        t.name for t in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], MailingList)
    assert fake_mailing_list.list_id in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(fake_mailing_list, client, detail_url, login_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailingListDetailWithDeleteView, fake_mailing_list)}"
    )
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_mailing_list, other_client, detail_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    fake_mailing_list.refresh_from_db()
    assert fake_mailing_list is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_mailing_list, owner_client, detail_url):
    """Tests :class:`web.views.MailingListDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailingListDetailWithDeleteView, fake_mailing_list)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + MailingListFilterView.URL_NAME))
    with pytest.raises(MailingList.DoesNotExist):
        fake_mailing_list.refresh_from_db()
