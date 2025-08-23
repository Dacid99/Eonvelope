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

"""Test module for :mod:`web.views.AttachmentDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Attachment
from web.views import AttachmentFilterView
from web.views.attachment_views.AttachmentDetailWithDeleteView import (
    AttachmentDetailWithDeleteView,
)


@pytest.mark.django_db
def test_get_noauth(fake_attachment, client, detail_url, login_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(AttachmentDetailWithDeleteView, fake_attachment))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AttachmentDetailWithDeleteView, fake_attachment)}"
    )
    assert fake_attachment.file_name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_attachment, other_client, detail_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(AttachmentDetailWithDeleteView, fake_attachment)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_attachment.file_name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_attachment, owner_client, detail_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(AttachmentDetailWithDeleteView, fake_attachment)
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/attachment/attachment_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Attachment)
    assert fake_attachment.file_name in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(fake_attachment, client, detail_url, login_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(detail_url(AttachmentDetailWithDeleteView, fake_attachment))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(AttachmentDetailWithDeleteView, fake_attachment)}"
    )
    fake_attachment.refresh_from_db()
    assert fake_attachment is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_attachment, other_client, detail_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(AttachmentDetailWithDeleteView, fake_attachment)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_attachment.refresh_from_db()
    assert fake_attachment is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_attachment, owner_client, detail_url):
    """Tests :class:`web.views.AttachmentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(AttachmentDetailWithDeleteView, fake_attachment)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + AttachmentFilterView.URL_NAME))
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()
