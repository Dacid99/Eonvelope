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

"""Test module for :mod:`web.views.MailboxDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.constants import EmailFetchingCriterionChoices
from core.models import Daemon, Mailbox
from core.utils.fetchers.exceptions import FetcherError
from web.views import MailboxFilterView
from web.views.mailbox_views.MailboxDetailWithDeleteView import (
    MailboxDetailWithDeleteView,
)


@pytest.mark.django_db
def test_get_noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    assert fake_mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert fake_mailbox.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert fake_mailbox.name in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + MailboxFilterView.URL_NAME))
    with pytest.raises(Mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_post_test_noauth(
    fake_mailbox, client, detail_url, login_url, mock_Mailbox_test_connection
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    mock_Mailbox_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_auth_other(
    fake_mailbox, other_client, detail_url, mock_Mailbox_test_connection
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    mock_Mailbox_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_success_auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_test_connection
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "action_result" in response.context
    assert "status" in response.context["action_result"]
    assert response.context["action_result"]["status"] is True
    assert "message" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["message"], str)
    assert "error" in response.context["action_result"]
    assert not response.context["action_result"]["error"]
    mock_Mailbox_test_connection.assert_called_once()


@pytest.mark.django_db
def test_post_test_failure_auth_owner(
    faker, fake_mailbox, owner_client, detail_url, mock_Mailbox_test_connection
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_test_connection.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "action_result" in response.context
    assert "status" in response.context["action_result"]
    assert response.context["action_result"]["status"] is False
    assert "message" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["message"], str)
    assert "error" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["error"], str)
    mock_Mailbox_test_connection.assert_called_once()
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_test_missing_action_auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_test_connection
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Mailbox_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_fetch_all_noauth(
    fake_mailbox, client, detail_url, login_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch_all_auth_other(
    fake_mailbox, other_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch_all_success_auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "action_result" in response.context
    assert "status" in response.context["action_result"]
    assert response.context["action_result"]["status"] is True
    assert "message" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["message"], str)
    assert "error" in response.context["action_result"]
    assert not response.context["action_result"]["error"]
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
def test_post_fetch_all_failure_auth_owner(
    faker, fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_fetch.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [t.name for t in response.templates]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "action_result" in response.context
    assert "status" in response.context["action_result"]
    assert response.context["action_result"]["status"] is False
    assert "message" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["message"], str)
    assert "error" in response.context["action_result"]
    assert isinstance(response.context["action_result"]["error"], str)
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_fetch_all_missing_action_auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_add_daemon_noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    assert Daemon.objects.count() == 1

    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    assert Daemon.objects.count() == 1


@pytest.mark.django_db
def test_post_add_daemon_auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    assert Daemon.objects.count() == 1

    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    assert Daemon.objects.count() == 1


@pytest.mark.django_db
def test_post_add_daemon_auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    assert Daemon.objects.count() == 1

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert Daemon.objects.count() == 2
    added_daemon = Daemon.objects.get(pk=2)
    assert response.url == added_daemon.get_absolute_edit_url()


@pytest.mark.django_db
def test_post_add_daemon_missing_action_auth_owner(
    fake_mailbox, owner_client, detail_url
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    assert Daemon.objects.count() == 1

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    assert Daemon.objects.count() == 1
