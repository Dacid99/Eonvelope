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

"""Test module for the :class:`UploadEmailView` view class."""

import os

import pytest
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework import status

from core.constants import SupportedEmailUploadFormats
from web.views import UploadEmailView


@pytest.fixture
def email_upload_payload(fake_file):
    """Random email file upload payload."""
    return {"file_format": "eml", "file": fake_file}


@pytest.fixture
def mock_celery_app(mocker):
    """Patches the celery current app."""
    return mocker.patch(
        "web.views.mailbox_views.UploadEmailView.current_app", autospec=True
    )


@pytest.mark.django_db
def test_get__noauth(fake_mailbox, client, detail_url, login_url):
    """Tests :class:`web.views.UploadEmailView` with an unauthenticated user client."""
    response = client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(login_url)
    assert response.url.endswith(f"?next={detail_url(UploadEmailView, fake_mailbox)}")


@pytest.mark.django_db
def test_get__auth_other(fake_mailbox, other_client, detail_url):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    response = other_client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_get__auth_owner(fake_mailbox, owner_client, detail_url):
    """Tests :class:`web.views.UploadEmailView` with the authenticated owner user client."""
    response = owner_client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response, HttpResponse)
    assert "web/mailbox/upload_email.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert "mailbox" in response.context


@pytest.mark.django_db
def test_get__auth_admin(fake_mailbox, admin_client, detail_url):
    """Tests :class:`web.views.UploadEmailView` with the authenticated admin user client."""
    response = admin_client.get(detail_url(UploadEmailView, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_post_upload__noauth(
    fake_mailbox,
    client,
    detail_url,
    login_url,
    mock_celery_app,
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
    mock_celery_app.send_task.assert_not_called()


@pytest.mark.django_db
def test_post_upload__auth_other(
    fake_mailbox,
    other_client,
    detail_url,
    mock_celery_app,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    response = other_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_celery_app.send_task.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("file_format", SupportedEmailUploadFormats.values)
def test_post_upload_mailbox__auth_owner(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_celery_app,
    email_upload_payload,
    file_format,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated owner user client."""

    def check_file_arg(*args, **kwargs):
        filepath_argument = kwargs["args"][0]
        assert os.path.exists(filepath_argument)
        with open(filepath_argument, "rb") as file:
            email_upload_payload["file"].seek(0)
            assert file.read() == email_upload_payload["file"].read()
        return mock_celery_app.send_task.return_value

    mock_celery_app.send_task.side_effect = check_file_arg
    email_upload_payload["file_format"] = file_format

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_302_FOUND
    assert isinstance(response, HttpResponseRedirect)
    assert response.url.startswith(fake_mailbox.get_absolute_url())
    mock_celery_app.send_task.assert_called_once()
    assert (
        mock_celery_app.send_task.call_args.args[0] == "core.tasks.process_emails_file"
    )
    assert (
        mock_celery_app.send_task.call_args.kwargs["args"][1]
        == email_upload_payload["file_format"]
    )
    assert mock_celery_app.send_task.call_args.kwargs["args"][2] == fake_mailbox.pk


@pytest.mark.django_db
def test_post_upload__auth_owner__bad_format(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_celery_app,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    email_upload_payload["file_format"] = "something"

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert "web/mailbox/upload_email.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert response.context["form"].errors
    assert "mailbox" in response.context
    mock_celery_app.send_task.assert_not_called()


@pytest.mark.django_db
def test_post_upload__auth_owner__bad_file(
    fake_mailbox,
    owner_client,
    detail_url,
    mock_celery_app,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated other user client."""
    mock_celery_app.send_task.return_value.get.side_effect = ValueError

    response = owner_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_200_OK
    assert "web/mailbox/upload_email.html" in [
        template.name for template in response.templates
    ]
    assert "form" in response.context
    assert response.context["form"].errors
    assert "mailbox" in response.context
    mock_celery_app.send_task.assert_called_once()


@pytest.mark.django_db
def test_post_upload__auth_admin(
    fake_mailbox,
    admin_client,
    detail_url,
    mock_celery_app,
    email_upload_payload,
):
    """Tests :class:`web.views.UploadEmailView` with the authenticated admin user client."""
    response = admin_client.post(
        detail_url(UploadEmailView, fake_mailbox), email_upload_payload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "404.html" in [template.name for template in response.templates]
    mock_celery_app.send_task.assert_not_called()
