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

"""Test module for :mod:`web.views.EmailDetailWithDeleteView`."""

import pytest
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from rest_framework import status

from core.models import Email
from core.utils.fetchers.exceptions import MailAccountError, MailboxError
from web.views import EmailDetailWithDeleteView, EmailFilterView


@pytest.mark.django_db
def test_get_noauth(fake_email, client, detail_url, login_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.get(detail_url(EmailDetailWithDeleteView, fake_email))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EmailDetailWithDeleteView, fake_email)}"
    )
    assert fake_email.message_id not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_other(fake_email, other_client, detail_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.get(detail_url(EmailDetailWithDeleteView, fake_email))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    assert fake_email.message_id not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_get_auth_owner(fake_email, owner_client, detail_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(EmailDetailWithDeleteView, fake_email))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert fake_email.message_id in response.content.decode("utf-8")
    assert 'srcdoc="' not in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_delete_noauth(fake_email, client, detail_url, login_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(EmailDetailWithDeleteView, fake_email), {"delete": ""}
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EmailDetailWithDeleteView, fake_email)}"
    )
    fake_email.refresh_from_db()
    assert fake_email is not None


@pytest.mark.django_db
def test_post_delete_auth_other(fake_email, other_client, detail_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email), {"delete": ""}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    fake_email.refresh_from_db()
    assert fake_email is not None


@pytest.mark.django_db
def test_post_delete_auth_owner(fake_email, owner_client, detail_url):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client."""
    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email), {"delete": ""}
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(reverse("web:" + EmailFilterView.URL_NAME))
    with pytest.raises(Email.DoesNotExist):
        fake_email.refresh_from_db()


@pytest.mark.django_db
def test_post_restore_noauth(
    fake_email, client, detail_url, login_url, mock_Email_restore_to_mailbox
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EmailDetailWithDeleteView, fake_email)}"
    )
    mock_Email_restore_to_mailbox.assert_not_called()


@pytest.mark.django_db
def test_post_restore_auth_other(
    fake_email, other_client, detail_url, mock_Email_restore_to_mailbox
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Email_restore_to_mailbox.assert_not_called()


@pytest.mark.django_db
def test_post_restore_auth_owner_success(
    fake_email, owner_client, detail_url, mock_Email_restore_to_mailbox
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Email_restore_to_mailbox.assert_called_once()


@pytest.mark.django_db
def test_post_restore_auth_owner_pop(
    fake_email,
    owner_client,
    detail_url,
    mock_Email_restore_to_mailbox,
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Email_restore_to_mailbox.side_effect = NotImplementedError

    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Email_restore_to_mailbox.assert_called_once()


@pytest.mark.django_db
def test_post_restore_auth_owner_no_file(
    fake_email,
    owner_client,
    detail_url,
    mock_Email_restore_to_mailbox,
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Email_restore_to_mailbox.side_effect = FileNotFoundError

    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Email_restore_to_mailbox.assert_called_once()


@pytest.mark.django_db
@pytest.mark.parametrize("error", [MailAccountError, MailboxError])
def test_post_restore_auth_owner_failure(
    fake_error_message,
    fake_email,
    owner_client,
    detail_url,
    mock_Email_restore_to_mailbox,
    error,
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case of failure.
    """
    mock_Email_restore_to_mailbox.side_effect = error(Exception(fake_error_message))

    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"restore": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.ERROR
    mock_Email_restore_to_mailbox.assert_called_once()
    assert fake_error_message in response.content.decode("utf-8")


@pytest.mark.django_db
def test_post_restore_missing_action_auth_owner(
    fake_email, owner_client, detail_url, mock_Email_restore_to_mailbox
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case the action is missing in the request.
    """
    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert isinstance(response, HttpResponse)
    mock_Email_restore_to_mailbox.assert_not_called()


@pytest.mark.django_db
def test_post_reprocess_noauth(
    fake_email, client, detail_url, login_url, mock_Email_reprocess
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with an unauthenticated user client."""
    response = client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"reprocess": ""},
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(
        f"?next={detail_url(EmailDetailWithDeleteView, fake_email)}"
    )
    mock_Email_reprocess.assert_not_called()


@pytest.mark.django_db
def test_post_reprocess_auth_other(
    fake_email, other_client, detail_url, mock_Email_reprocess
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"reprocess": ""},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_Email_reprocess.assert_not_called()


@pytest.mark.django_db
def test_post_reprocess_auth_owner_success(
    fake_email, owner_client, detail_url, mock_Email_reprocess
):
    """Tests :class:`web.views.EmailDetailWithDeleteView` with the authenticated owner user client
    in case of success.
    """
    response = owner_client.post(
        detail_url(EmailDetailWithDeleteView, fake_email),
        {"reprocess": ""},
    )

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/email/email_detail.html" in [
        template.name for template in response.templates
    ]
    assert "object" in response.context
    assert isinstance(response.context["object"], Email)
    assert "messages" in response.context
    assert len(response.context["messages"]) == 1
    for mess in response.context["messages"]:
        assert mess.level == messages.SUCCESS
    mock_Email_reprocess.assert_called_once()
