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

"""Test module for :mod:`web.views.CorrespondentDetailWithDeleteView`."""

import pytest
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Correspondent
from web.views.correspondent_views.CorrespondentDetailWithDeleteView import (
    CorrespondentDetailWithDeleteView,
)
from web.views.correspondent_views.CorrespondentFilterView import (
    CorrespondentFilterView,
)


@pytest.mark.django_db
def test_get_noauth(fake_correspondent, client, detail_url, login_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)}"
    )
    assert fake_correspondent.email_address not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_other(fake_correspondent, other_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_correspondent.email_address not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_owner(fake_correspondent, owner_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/correspondent/correspondent_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Correspondent)
    assert "latest_correspondentemails" in response.context
    assert isinstance(response.context["latest_correspondentemails"], QuerySet)
    assert fake_correspondent.email_address in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_admin(fake_correspondent, admin_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.get(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_correspondent.email_address not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_delete_noauth(fake_correspondent, client, detail_url, login_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)}"
    )
    fake_correspondent.refresh_from_db()
    assert fake_correspondent is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_correspondent, other_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_correspondent.refresh_from_db()
    assert fake_correspondent is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_correspondent, owner_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + CorrespondentFilterView.URL_NAME))
    with pytest.raises(Correspondent.DoesNotExist):
        fake_correspondent.refresh_from_db()


@pytest.mark.django_db
def test_post_delete_auth_admin(fake_correspondent, admin_client, detail_url):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_correspondent.refresh_from_db()
    assert fake_correspondent is not None


@pytest.mark.django_db
def test_post_share_to_nextcloud_noauth(
    fake_correspondent,
    client,
    detail_url,
    login_url,
    mock_Correspondent_share_to_nextcloud,
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"share": "nextcloud"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(CorrespondentDetailWithDeleteView, fake_correspondent)}"
    )
    mock_Correspondent_share_to_nextcloud.assert_not_called()


@pytest.mark.django_db
def test_post_share_to_nextcloud_auth_other(
    fake_correspondent, other_client, detail_url, mock_Correspondent_share_to_nextcloud
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"share": "nextcloud"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Correspondent_share_to_nextcloud.assert_not_called()


@pytest.mark.django_db
def test_post_share_to_nextcloud_success_auth_owner(
    fake_correspondent, owner_client, detail_url, mock_Correspondent_share_to_nextcloud
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"share": "nextcloud"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/correspondent/correspondent_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Correspondent)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Correspondent_share_to_nextcloud.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "error",
    [
        ConnectionError,
        PermissionError,
        ValueError,
        RuntimeError,
    ],
)
def test_post_share_to_nextcloud_failure_auth_owner(
    fake_error_message,
    fake_correspondent,
    owner_client,
    detail_url,
    mock_Correspondent_share_to_nextcloud,
    error,
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Correspondent_share_to_nextcloud.side_effect = error(fake_error_message)

    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"share": "nextcloud"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/correspondent/correspondent_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Correspondent)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Correspondent_share_to_nextcloud.assert_called_once()
    assert fake_error_message in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_share_to_nextcloud_missing_action_auth_owner(
    fake_correspondent, owner_client, detail_url, mock_Correspondent_share_to_nextcloud
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Correspondent_share_to_nextcloud.assert_not_called()


@pytest.mark.django_db
def test_post_share_missing_value_auth_owner(
    fake_correspondent,
    owner_client,
    detail_url,
    mock_Correspondent_share_to_nextcloud,
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent), {"share": ""}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Correspondent_share_to_nextcloud.assert_not_called()


@pytest.mark.django_db
def test_post_share_to_nextcloud_auth_admin(
    fake_correspondent, admin_client, detail_url, mock_Correspondent_share_to_nextcloud
):
    """Tests :class:`web.views.CorrespondentDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(CorrespondentDetailWithDeleteView, fake_correspondent),
        {"share": "nextcloud"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Correspondent_share_to_nextcloud.assert_not_called()
