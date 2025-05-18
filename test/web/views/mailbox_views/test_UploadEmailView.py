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

"""Test module for the :class:`UploadEmailView` view class."""

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from test.api.v1.views.test_MailboxViewSet_custom_actions import (
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
)
from web.views import UploadEmailView


@pytest.fixture
def email_upload_payload(faker, fake_file) -> dict:
    return {"file_format": "eml", "file": fake_file}


@pytest.mark.django_db
def test_get_noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.UploadEmailView` with an unauthenticated user client."""
    response = client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={detail_url(UploadEmailView, fake_mailbox)}")


@pytest.mark.django_db
def test_get_auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    response = other_client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_get_auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.UploadEmailView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/upload_email.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert "mailbox" in response.context


@pytest.mark.django_db
def test_post_upload_noauth(
    fake_mailbox,
    client,
    detail_url,
    login_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with an unauthenticated user client."""
    response = client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={detail_url(UploadEmailView, fake_mailbox)}")
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_Mailbox_add_from_mailbox_file.assert_not_called()


@pytest.mark.django_db
def test_post_upload_auth_other(
    fake_mailbox,
    other_client,
    detail_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [t.name for t in response.templates]
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_Mailbox_add_from_mailbox_file.assert_not_called()


@pytest.mark.django_db
def test_post_upload_eml_auth_owner(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated owner user client."""
    email_upload_payload["file_format"] = "eml"

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(fake_mailbox.get_absolute_url())
    mock_Email_create_from_email_bytes.assert_called_once_with(
        email_upload_payload["file"].getvalue(), mailbox=fake_mailbox
    )
    mock_Mailbox_add_from_mailbox_file.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "mailbox_file_format", ["mbox", "maildir", "mh", "babyl", "mmdf"]
)
def test_post_upload_mailbox_auth_owner(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
    mailbox_file_format,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated owner user client."""
    email_upload_payload["file_format"] = mailbox_file_format

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(fake_mailbox.get_absolute_url())
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_Mailbox_add_from_mailbox_file.assert_called_once_with(
        fake_mailbox, email_upload_payload["file"].getvalue(), mailbox_file_format
    )


@pytest.mark.django_db
def test_post_upload_auth_owner_bad_format(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    email_upload_payload["file_format"] = "something"

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert "web/mailbox/upload_email.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert "mailbox" in response.context
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_Mailbox_add_from_mailbox_file.assert_not_called()


@pytest.mark.django_db
def test_post_upload_auth_owner_bad_file(
    faker,
    fake_mailbox,
    owner_client,
    detail_url,
    mock_Email_create_from_email_bytes,
    mock_Mailbox_add_from_mailbox_file,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    email_upload_payload["file"] = faker.sentence().encode()

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert "web/mailbox/upload_email.html" in [t.name for t in response.templates]
    assert "form" in response.context
    assert "mailbox" in response.context
    mock_Email_create_from_email_bytes.assert_not_called()
    mock_Mailbox_add_from_mailbox_file.assert_not_called()
