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

"""Test module for :mod:`web.views.Mailbox_views.MailboxDetailWithDeleteView`."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.constants import EmailFetchingCriterionChoices
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import FetcherError
from web.views.mailbox_views.MailboxDetailWithDeleteView import (
    MailboxDetailWithDeleteView,
)
from web.views.mailbox_views.MailboxFilterView import MailboxFilterView


@pytest.mark.django_db
def test_get_noauth(mailboxModel, client, detail_url, login_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxDetailWithDeleteView, mailboxModel))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, mailboxModel)}"
    )
    assert mailboxModel.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_other(mailboxModel, other_client, detail_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxDetailWithDeleteView, mailboxModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert mailboxModel.name not in response.content.decode()


@pytest.mark.django_db
def test_get_auth_owner(mailboxModel, owner_client, detail_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxDetailWithDeleteView, mailboxModel))

    assert response.status_code == status.HTTP_200_OK
    assert mailboxModel.name in response.content.decode()


@pytest.mark.django_db
def test_post_delete_noauth(mailboxModel, client, detail_url, login_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, mailboxModel)}"
    )
    mailboxModel.refresh_from_db()
    assert mailboxModel is not None


@pytest.mark.django_db
def test_post_delete_auth_other(mailboxModel, other_client, detail_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(mailboxModel, owner_client, detail_url):
    """Tests :class:`web.views.mailbox_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"delete": "Delete"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + MailboxFilterView.URL_NAME))
    with pytest.raises(MailboxModel.DoesNotExist):
        mailboxModel.refresh_from_db()


@pytest.mark.django_db
def test_post_test_noauth(
    mailboxModel, client, detail_url, login_url, mock_MailboxModel_test_connection
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, mailboxModel)}"
    )
    mock_MailboxModel_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_auth_other(
    mailboxModel, other_client, detail_url, mock_MailboxModel_test_connection
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_test_connection.assert_not_called()


@pytest.mark.django_db
def test_post_test_success_auth_owner(
    mailboxModel, owner_client, detail_url, mock_MailboxModel_test_connection
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_MailboxModel_test_connection.assert_called_once()


@pytest.mark.django_db
def test_post_test_failure_auth_owner(
    faker, mailboxModel, owner_client, detail_url, mock_MailboxModel_test_connection
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_MailboxModel_test_connection.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"test": "Test"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_MailboxModel_test_connection.assert_called_once()
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_fetch_all_noauth(
    mailboxModel, client, detail_url, login_url, mock_MailboxModel_fetch
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, mailboxModel)}"
    )
    mock_MailboxModel_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch_all_auth_other(
    mailboxModel, other_client, detail_url, mock_MailboxModel_fetch
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch_all_success_auth_owner(
    mailboxModel, owner_client, detail_url, mock_MailboxModel_fetch
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_MailboxModel_fetch.assert_called_once_with(
        mailboxModel, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
def test_post_fetch_all_failure_auth_owner(
    faker, mailboxModel, owner_client, detail_url, mock_MailboxModel_fetch
):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_MailboxModel_fetch.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"fetch_all": "Fetch contents"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    mock_MailboxModel_fetch.assert_called_once_with(
        mailboxModel, EmailFetchingCriterionChoices.ALL
    )
    assert fake_error_message in response.content.decode()


@pytest.mark.django_db
def test_post_add_daemon_noauth(mailboxModel, client, detail_url, login_url):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    assert DaemonModel.objects.count() == 1

    response = client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, mailboxModel)}"
    )
    assert DaemonModel.objects.count() == 1


@pytest.mark.django_db
def test_post_add_daemon_auth_other(mailboxModel, other_client, detail_url):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated other user client."""
    assert DaemonModel.objects.count() == 1

    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert DaemonModel.objects.count() == 1


@pytest.mark.django_db
def test_post_add_daemon_auth_owner(mailboxModel, owner_client, detail_url):
    """Tests :class:`web.views.account_views.MailboxDetailWithDeleteView.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    assert DaemonModel.objects.count() == 1

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, mailboxModel),
        {"add_daemon": "Add daemon"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert DaemonModel.objects.count() == 2
    added_daemon = DaemonModel.objects.get(pk=2)
    assert response.url == added_daemon.get_absolute_edit_url()
