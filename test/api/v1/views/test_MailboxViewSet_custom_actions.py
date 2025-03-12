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
from core.models.DaemonModel import DaemonModel
from core.models.EMailModel import EMailModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


@pytest.fixture(name="mock_MailboxModel_test_connection")
def fixture_mock_MailboxModel_test_connection(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.MailboxModel.test_connection", autospec=True
    )


@pytest.fixture(name="mock_MailboxModel_fetch")
def fixture_mock_MailboxModel_fetch(mocker):
    return mocker.patch("api.v1.views.MailboxViewSet.MailboxModel.fetch", autospec=True)


@pytest.fixture(name="mock_EMailModel_createFromEmailBytes")
def fixture_mock_EMailModel_createFromEmailBytes(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.EMailModel.createFromEmailBytes", autospec=True
    )


@pytest.fixture(name="mock_MailboxModel_addFromMailboxFile")
def fixture_mock_MailboxModel_addFromMailboxFile(mocker):
    return mocker.patch(
        "api.v1.views.MailboxViewSet.MailboxModel.addFromMailboxFile", autospec=True
    )


@pytest.fixture(name="fake_file")
def fixture_fake_file(faker):
    fake_file_content = faker.text().encode()
    return BytesIO(fake_file_content)


@pytest.mark.django_db
def test_add_daemon_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with an unauthenticated user client."""
    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 1
    assert DaemonModel.objects.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 1
    assert DaemonModel.objects.all().count() == 1


@pytest.mark.django_db
def test_add_daemon_auth_other(mailboxModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with the authenticated other user client."""
    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 1
    assert DaemonModel.objects.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 1
    assert DaemonModel.objects.all().count() == 1


@pytest.mark.django_db
def test_add_daemon_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.add_daemon` action with the authenticated owner user client."""
    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 1
    assert DaemonModel.objects.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_ADD_DAEMON, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )

    assert DaemonModel.objects.filter(mailbox=mailboxModel).count() == 2
    assert DaemonModel.objects.all().count() == 2


@pytest.mark.django_db
def test_test_mailbox_noauth(
    mailboxModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with an unauthenticated user client."""
    previous_is_healthy = mailboxModel.is_healthy

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_MailboxModel_test_connection.assert_not_called()
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_test_mailbox_auth_other(
    mailboxModel,
    other_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated other user client."""
    previous_is_healthy = mailboxModel.is_healthy

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_test_connection.assert_not_called()
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_test_mailbox_success_auth_owner(
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_test_connection,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test_mailbox` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    assert response.data["result"] is True
    assert "error" not in response.data
    mock_MailboxModel_test_connection.assert_called_once_with(mailboxModel)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_connection_side_effect", [MailboxError, MailAccountError]
)
def test_test_mailbox_failure_auth_owner(
    faker,
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_test_connection,
    test_connection_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.test` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_MailboxModel_test_connection.side_effect = test_connection_side_effect(
        fake_error_message
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TEST, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    assert response.data["result"] is False
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_MailboxModel_test_connection.assert_called_once_with(mailboxModel)


@pytest.mark.django_db
def test_fetch_all_noauth(
    mailboxModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with an unauthenticated user client."""
    assert EMailModel.objects.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_MailboxModel_fetch.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_fetch_all_auth_other(
    mocker,
    mailboxModel,
    other_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated other user client."""
    assert EMailModel.objects.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_fetch.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_fetch_all_success_auth_owner(
    mocker,
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_fetch,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    assert "error" not in response.data
    mock_MailboxModel_fetch.assert_called_once_with(
        mailboxModel, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
@pytest.mark.parametrize("fetch_side_effect", [MailboxError, MailAccountError])
def test_fetch_all_failure_auth_owner(
    faker,
    mailboxModel,
    owner_apiClient,
    mock_MailboxModel_fetch,
    custom_detail_action_url,
    fetch_side_effect,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.fetch_all` action with the authenticated owner user client."""
    fake_error_message = faker.sentence()
    mock_MailboxModel_fetch.side_effect = fetch_side_effect(fake_error_message)

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_FETCH_ALL, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    assert "error" in response.data
    assert fake_error_message in response.data["error"]
    mock_MailboxModel_fetch.assert_called_once_with(
        mailboxModel, EmailFetchingCriterionChoices.ALL
    )


@pytest.mark.django_db
def test_upload_eml_noauth(
    mailboxModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_EMailModel_createFromEmailBytes,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with an unauthenticated user client."""
    assert EMailModel.objects.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, mailboxModel
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_eml_auth_other(
    mailboxModel,
    other_apiClient,
    custom_detail_action_url,
    mock_EMailModel_createFromEmailBytes,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated other user client."""
    assert EMailModel.objects.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, mailboxModel
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_eml_auth_owner(
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailModel_createFromEmailBytes,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated owner user client."""

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, mailboxModel
        ),
        {"eml": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    mock_EMailModel_createFromEmailBytes.assert_called_once_with(
        fake_file.getvalue(), mailboxModel
    )


@pytest.mark.django_db
def test_upload_eml_no_file_auth_owner(
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_EMailModel_createFromEmailBytes,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_eml` action with the authenticated owner user client."""
    assert EMailModel.objects.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_EML, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_EMailModel_createFromEmailBytes.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_noauth(
    faker,
    mailboxModel,
    noauth_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with an unauthenticated user client."""
    fake_format = faker.word()

    assert EMailModel.objects.all().count() == 1

    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_MailboxModel_addFromMailboxFile.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_auth_other(
    faker,
    mailboxModel,
    other_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated other user client."""
    fake_format = faker.word()

    assert EMailModel.objects.all().count() == 1

    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_MailboxModel_addFromMailboxFile.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_auth_owner(
    faker,
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        response.data["mailbox"] == MailboxViewSet.serializer_class(mailboxModel).data
    )
    mock_MailboxModel_addFromMailboxFile.assert_called_once_with(
        mailboxModel, fake_file.getvalue(), fake_format
    )


@pytest.mark.django_db
def test_upload_mailbox_no_file_auth_owner(
    faker,
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    fake_format = faker.word()

    assert EMailModel.objects.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"format": fake_format},
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_MailboxModel_addFromMailboxFile.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_no_format_auth_owner(
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    assert EMailModel.objects.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"file": fake_file},
        format="multipart",
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    mock_MailboxModel_addFromMailboxFile.assert_not_called()
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_upload_mailbox_bad_format_auth_owner(
    faker,
    mailboxModel,
    owner_apiClient,
    custom_detail_action_url,
    mock_MailboxModel_addFromMailboxFile,
    fake_file,
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.upload_mailbox` action with the authenticated owner user client."""
    mock_MailboxModel_addFromMailboxFile.side_effect = ValueError
    fake_format = faker.word()

    assert EMailModel.objects.all().count() == 1

    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_UPLOAD_MAILBOX, mailboxModel
        ),
        {"file": fake_file, "format": fake_format},
        format="multipart",
    )

    assert response.status_code == status.HTTP_415_UNSUPPORTED_MEDIA_TYPE
    mock_MailboxModel_addFromMailboxFile.assert_called_once_with(
        mailboxModel, fake_file.getvalue(), fake_format
    )
    assert EMailModel.objects.all().count() == 1
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_toggle_favorite_noauth(
    mailboxModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    mailboxModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    mailboxModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.MailboxViewSet.MailboxViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            MailboxViewSet, MailboxViewSet.URL_NAME_TOGGLE_FAVORITE, mailboxModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is True
