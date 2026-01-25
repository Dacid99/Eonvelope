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

"""Test module for :mod:`web.views.DaemonDetailWithDeleteView`."""

import pytest
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Daemon
from web.views import DaemonDetailWithDeleteView, DaemonFilterView


@pytest.mark.django_db
def test_get__noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    assert fake_daemon.mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    assert fake_daemon.mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert fake_daemon.mailbox.name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_admin(fake_daemon, admin_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    assert fake_daemon.mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_delete__noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete__auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_delete__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + DaemonFilterView.URL_NAME))
    with pytest.raises(Daemon.DoesNotExist):
        fake_daemon.refresh_from_db()


@pytest.mark.django_db
def test_post_delete__auth_admin(fake_daemon, admin_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon is not None


@pytest.mark.django_db
def test_post_test__noauth(
    fake_daemon, client, detail_url, login_url, mock_Daemon_test
):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__auth_other(fake_daemon, other_client, detail_url, mock_Daemon_test):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__success__auth_owner(
    fake_daemon, owner_client, detail_url, mock_Daemon_test
):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Daemon_test.assert_called_once()


@pytest.mark.django_db
def test_post_test__failure__auth_owner(
    fake_error_message, fake_daemon, owner_client, detail_url, mock_Daemon_test
):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Daemon_test.side_effect = Exception(fake_error_message)

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Daemon_test.assert_called_once()
    assert fake_error_message in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_test__missing_action__auth_owner(
    fake_daemon, owner_client, detail_url, mock_Daemon_test
):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__auth_admin(fake_daemon, admin_client, detail_url, mock_Daemon_test):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Daemon_test.assert_not_called()


@pytest.mark.django_db
def test_post_start__noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_start__auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated other user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(response, HttpResponse)
    assert "404.html" in [template.name for template in response.templates]
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_start__success__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_post_start__failure__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client."""
    assert fake_daemon.celery_task.enabled is True

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.WARNING
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_post_start__missing_action__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = owner_client.post(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_start__auth_admin(fake_daemon, admin_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated admin user client."""
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = admin_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"start_daemon": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert isinstance(response, HttpResponse)
    assert "404.html" in [template.name for template in response.templates]
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_stop__noauth(fake_daemon, client, detail_url, login_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with an unauthenticated user client."""
    assert fake_daemon.celery_task.enabled is True

    response = client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(DaemonDetailWithDeleteView, fake_daemon)}"
    )
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_post_stop__auth_other(fake_daemon, other_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated other user client."""
    assert fake_daemon.celery_task.enabled is True

    response = other_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_post_stop__success__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    assert fake_daemon.celery_task.enabled is True

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_stop__failure__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    fake_daemon.celery_task.enabled = False
    fake_daemon.celery_task.save(update_fields=["enabled"])

    assert fake_daemon.celery_task.enabled is False

    response = owner_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/daemon/daemon_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Daemon)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.WARNING
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is False


@pytest.mark.django_db
def test_post_stop__missing_action__auth_owner(fake_daemon, owner_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    assert fake_daemon.celery_task.enabled is True

    response = owner_client.post(detail_url(DaemonDetailWithDeleteView, fake_daemon))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True


@pytest.mark.django_db
def test_post_stop__auth_admin(fake_daemon, admin_client, detail_url):
    """Tests :class:`web.views.DaemonDetailWithDeleteView` with the authenticated admin user client."""
    assert fake_daemon.celery_task.enabled is True

    response = admin_client.post(
        detail_url(DaemonDetailWithDeleteView, fake_daemon),
        {"stop_daemon": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert isinstance(response, HttpResponse)
    fake_daemon.refresh_from_db()
    assert fake_daemon.celery_task.enabled is True
