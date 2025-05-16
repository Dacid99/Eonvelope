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

"""Test module for :mod:`api.v1.views.MailboxViewSet`'s custom actions."""

from __future__ import annotations

from io import BytesIO

import pytest
from rest_framework import status

from api.v1.views.MailboxViewSet import MailboxViewSet
from core.constants import EmailFetchingCriterionChoices
from core.models.Daemon import Daemon
from core.models.Email import Email
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


@pytest.fixture
def mock_Mailbox_test_connection(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Mailbox.test_connection", autospec=True
    )


@pytest.fixture
def mock_Mailbox_fetch(mocker):
    return mocker.patch("api.v1.views.MailboxViewSet.Mailbox.fetch", autospec=True)


@pytest.fixture
def mock_Email_createFromEmailBytes(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Email.createFromEmailBytes", autospec=True
    )


@pytest.fixture
def mock_Mailbox_addFromMailboxFile(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.Mailbox.addFromMailboxFile", autospec=True
    )


@pytest.mark.django_db
def test_add_daemon_noauth(fake_mailbox, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with an unauthenticated user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    assert fake_mailbox.daemons.all().count() == 1


@pytest.mark.django_db
def test_add_daemon_auth_other(fake_mailbox, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with the authenticated other user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    assert fake_mailbox.daemons.all().count() == 1


@pytest.mark.django_db
def test_add_daemon_auth_owner(fake_mailbox, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with the authenticated owner user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )

    assert fake_mailbox.daemons.all().count() == 2


@pytest.mark.django_db
def test_test_mailbox_noauth(
    fake_mailbox,
    noauth_apiClient,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with an unauthenticated user client."""
    previous_is_healthy = fake_mailbox.is_healthy

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_test_connection.assert_not_called()
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_test_mailbox_auth_other(
    fake_mailbox,
    other_apiClient,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated other user client."""
    previous_is_healthy = fake_mailbox.is_healthy

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_test_connection.assert_not_called()
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_test_mailbox_success_auth_owner(
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert response.data["result"] is True
    assert "error" not in response.data
    mock_Mailbox_test_connection.assert_called_once_with(fake_mailbox)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_connection_side_effect", [MailboxError, MailAccountError]
)
def test_test_mailbox_failure_auth_owner(
    faker,
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_test_connection,
    test_connection_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_test_connection.side_effect = test_connection_side_effect(
        fake_error_message
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert response.data["result"] is False
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Mailbox_test_connection.assert_called_once_with(fake_mailbox)


@pytest.mark.django_db
def test_fetch_all_noauth(
    fake_mailbox,
    noauth_apiClient,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with an unauthenticated user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_fetch.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_fetch_all_auth_other(
    fake_mailbox,
    other_apiClient,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated other user client."""
    assert fake_mailbox.daemons.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_fetch.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_fetch_all_success_auth_owner(
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert "error" not in response.data
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
@pytest.mark.parametrize("fetch_side_effect", [MailboxError, MailAccountError])
def test_fetch_all_failure_auth_owner(
    faker,
    fake_mailbox,
    owner_apiClient,
    mock_Mailbox_fetch,
    custom_detail_action_url,
    fetch_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_Mailbox_fetch.side_effect = fetch_side_effect(fake_error_message)

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_Mailbox_fetch.assert_called_once_with(
        fake_mailbox, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
def test_upload_eml_noauth(
    fake_file,
    fake_mailbox,
    noauth_apiClient,
    custom_detail_action_url,
    mock_Email_createFromEmailBytes,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with an unauthenticated user client."""
    assert fake_mailbox.emails.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, fake_mailbox
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Email_createFromEmailBytes.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_eml_auth_other(
    fake_file,
    fake_mailbox,
    other_apiClient,
    custom_detail_action_url,
    mock_Email_createFromEmailBytes,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated other user client."""
    assert fake_mailbox.emails.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, fake_mailbox
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Email_createFromEmailBytes.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_eml_auth_owner(
    fake_file,
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Email_createFromEmailBytes,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated owner user client."""

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, fake_mailbox
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    mock_Email_createFromEmailBytes.assert_called_once_with(
        fake_file.getvalue(), fake_mailbox
    )


@pytest.mark.django_db
def test_upload_eml_no_file_auth_owner(
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Email_createFromEmailBytes,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated owner user client."""
    assert fake_mailbox.emails.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_Email_createFromEmailBytes.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_noauth(
    faker,
    fake_mailbox,
    noauth_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with an unauthenticated user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_Mailbox_addFromMailboxFile.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_auth_other(
    faker,
    fake_mailbox,
    other_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated other user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_Mailbox_addFromMailboxFile.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_auth_owner(
    faker,
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(fake_mailbox).data
    )
    mock_Mailbox_addFromMailboxFile.assert_called_once_with(
        fake_mailbox, fake_file.getvalue(), fake_format
    )


@pytest.mark.django_db
def test_upload_mailbox_no_file_auth_owner(
    faker,
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"format": fake_format},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_Mailbox_addFromMailboxFile.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_no_format_auth_owner(
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    assert fake_mailbox.emails.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_Mailbox_addFromMailboxFile.assert_not_called()
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_bad_format_auth_owner(
    faker,
    fake_mailbox,
    owner_apiClient,
    custom_detail_action_url,
    mock_Mailbox_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    mock_Mailbox_addFromMailboxFile.side_effect = ValueError
    fake_format = faker.word()

    assert fake_mailbox.emails.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, fake_mailbox
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    mock_Mailbox_addFromMailboxFile.assert_called_once_with(
        fake_mailbox, fake_file.getvalue(), fake_format
    )
    assert fake_mailbox.emails.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    fake_mailbox, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    fake_mailbox, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    fake_mailbox, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, fake_mailbox
        )
    )

    assert response.status_code == status.HTTP_200_OK
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.is_favorite is True
