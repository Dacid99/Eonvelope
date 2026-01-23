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

"""Test module for :mod:`web.views.MailboxDetailWithDeleteView`."""

import pytest
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.constants import EmailFetchingCriterionChoices
from core.models import Mailbox
from core.utils.fetchers.exceptions import FetcherError
from web.views import MailboxFilterView
from web.views.mailbox_views.MailboxDetailWithDeleteView import (
    MailboxDetailWithDeleteView,
)


@pytest.mark.django_db
def test_get__noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert isinstance(response.context["latest_emails"], QuerySet)
    assert fake_mailbox.name in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get__auth_admin(fake_mailbox, admin_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_mailbox.name not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_delete__noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": ""},
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
def test_post_delete__auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_delete__auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + MailboxFilterView.URL_NAME))
    with pytest.raises(Mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()


@pytest.mark.django_db
def test_post_delete__auth_admin(fake_mailbox, admin_client, detail_url):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"delete": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox is not None


@pytest.mark.django_db
def test_post_test__noauth(
    fake_mailbox, client, detail_url, login_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    mock_Mailbox_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__auth_other(
    fake_mailbox, other_client, detail_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Mailbox_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__success__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Mailbox_test.assert_called_once()


@pytest.mark.django_db
def test_post_test__failure__auth_owner(
    fake_error_message, fake_mailbox, owner_client, detail_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Mailbox_test.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Mailbox_test.assert_called_once()
    assert fake_error_message in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_test__missing_action__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Mailbox_test.assert_not_called()


@pytest.mark.django_db
def test_post_test__auth_admin(
    fake_mailbox, admin_client, detail_url, mock_Mailbox_test
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"test": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Mailbox_test.assert_not_called()


@pytest.mark.django_db
def test_post_fetch__noauth(
    fake_mailbox, client, detail_url, login_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": EmailFetchingCriterionChoices.ALL.value},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(MailboxDetailWithDeleteView, fake_mailbox)}"
    )
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch__auth_other(
    fake_mailbox, other_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": EmailFetchingCriterionChoices.ALL.value},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch__success__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": EmailFetchingCriterionChoices.ALL.value},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL, ""
    )


@pytest.mark.django_db
def test_post_fetch__no_criterion__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case no criterion is given.
    """
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL, ""
    )


@pytest.mark.django_db
def test_post_fetch__bad_criterion__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case an unavailable criterion is given.
    """
    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": "WEIRD"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.WARNING
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch__failure__auth_owner(
    fake_error_message, fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Mailbox_fetch.side_effect = FetcherError(fake_error_message)

    response = owner_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": EmailFetchingCriterionChoices.ALL.value},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/mailbox_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Mailbox)
    assert "latest_emails" in response.context
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL, ""
    )
    assert fake_error_message in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_fetch__missing_action__auth_owner(
    fake_mailbox, owner_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(detail_url(MailboxDetailWithDeleteView, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Mailbox_fetch.assert_not_called()


@pytest.mark.django_db
def test_post_fetch__auth_admin(
    fake_mailbox, admin_client, detail_url, mock_Mailbox_fetch
):
    """Tests :class:`web.views.MailboxDetailWithDeleteView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(MailboxDetailWithDeleteView, fake_mailbox),
        {"fetch": EmailFetchingCriterionChoices.ALL.value},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Mailbox_fetch.assert_not_called()
