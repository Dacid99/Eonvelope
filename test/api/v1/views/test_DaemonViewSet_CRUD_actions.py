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

"""Test module for :mod:`api.v1.views.DaemonViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from django.forms import model_to_dict
from rest_framework import status

from api.v1.views import DaemonViewSet
from core.models import Daemon


@pytest.mark.django_db
def test_list_noauth(fake_daemon, noauth_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "results" not in response.data


@pytest.mark.django_db
def test_list_auth_other(fake_daemon, other_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_daemon, owner_api_client, list_url):
    """Tests the list method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client."""
    response = owner_api_client.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(fake_daemon, noauth_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.get(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "logfile_size" not in response.data


@pytest.mark.django_db
def test_get_auth_other(fake_daemon, other_api_client, detail_url):
    """Tests the get method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.get(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(fake_daemon, owner_api_client, detail_url):
    """Tests the list method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client."""
    response = owner_api_client.get(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["logfile_size"] == fake_daemon.logfile_size


@pytest.mark.django_db
def test_patch_noauth(
    fake_daemon, noauth_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.patch(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "logfile_size" not in response.data
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_patch_auth_other(
    fake_daemon, other_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.patch(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "logfile_size" not in response.data
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_patch_auth_owner(
    fake_daemon, owner_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the patch method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_api_client.patch(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["logfile_size"] == daemon_with_interval_payload["logfile_size"]
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size == daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_put_noauth(
    fake_daemon, noauth_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.put(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "logfile_size" not in response.data
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_put_auth_other(
    fake_daemon, other_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.put(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "logfile_size" not in response.data
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size != daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_put_auth_owner(
    fake_daemon, owner_api_client, daemon_with_interval_payload, detail_url
):
    """Tests the put method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_api_client.put(
        detail_url(DaemonViewSet, fake_daemon),
        data=daemon_with_interval_payload,
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["logfile_size"] == daemon_with_interval_payload["logfile_size"]
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size == daemon_with_interval_payload["logfile_size"]


@pytest.mark.django_db
def test_post_noauth(noauth_api_client, daemon_with_interval_payload, list_url):
    """Tests the post method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.post(
        list_url(DaemonViewSet),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "logfile_size" not in response.data
    with pytest.raises(Daemon.DoesNotExist):
        Daemon.objects.get(logfile_size=daemon_with_interval_payload["logfile_size"])


@pytest.mark.django_db
def test_post_auth_other(other_api_client, daemon_with_interval_payload, list_url):
    """Tests the post method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.post(
        list_url(DaemonViewSet),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "mailbox" in response.data
    assert "logfile_size" not in response.data
    with pytest.raises(Daemon.DoesNotExist):
        Daemon.objects.get(logfile_size=daemon_with_interval_payload["logfile_size"])


@pytest.mark.django_db
def test_post_auth_owner(
    owner_api_client, owner_user, daemon_with_interval_payload, list_url
):
    """Tests the post method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client."""
    response = owner_api_client.post(
        list_url(DaemonViewSet),
        data=daemon_with_interval_payload,
        format="json",
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert "logfile_size" in response.data
    assert response.data["logfile_size"] == daemon_with_interval_payload["logfile_size"]
    posted_daemon = Daemon.objects.get(
        fetching_criterion=daemon_with_interval_payload["fetching_criterion"],
        mailbox=daemon_with_interval_payload["mailbox"],
    )
    assert posted_daemon is not None
    assert posted_daemon.mailbox.account.user == owner_user


@pytest.mark.django_db
def test_post_duplicate_auth_owner(fake_daemon, owner_api_client, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet` with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(fake_daemon)
    payload.pop("id")
    clean_payload = {key: value for key, value in payload.items() if value is not None}

    response = owner_api_client.post(list_url(DaemonViewSet), data=clean_payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_noauth(fake_daemon, noauth_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.DaemonViewSet` with an unauthenticated user client."""
    response = noauth_api_client.delete(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_daemon, other_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.DaemonViewSet` with the authenticated other user client."""
    response = other_api_client.delete(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_daemon.refresh_from_db()
    assert fake_daemon.logfile_size is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_daemon, owner_api_client, detail_url):
    """Tests the delete method on :class:`api.v1.views.DaemonViewSet` with the authenticated owner user client."""
    response = owner_api_client.delete(detail_url(DaemonViewSet, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(fake_daemon.DoesNotExist):
        fake_daemon.refresh_from_db()
