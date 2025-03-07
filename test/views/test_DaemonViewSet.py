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

"""Test module for :mod:`api.v1.views.AccountViewSet`.

Fixtures:
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_daemonModel`: Creates an mailbox in `accountModel`.
    :func:`fixture_mailboxPayload`: Creates clean :class:`core.models.DaemonModel.DaemonModel` payload for a patch, post or put request.

"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.DaemonViewSet import DaemonViewSet
from core.models.DaemonModel import DaemonModel

from .test_AccountViewSet import fixture_accountModel
from .test_MailboxViewSet import fixture_mailboxModel


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture(name="daemonModel")
def fixture_daemonModel(faker, mailboxModel) -> DaemonModel:
    """Creates an :class:`core.models.DaemonModel.DaemonModel` owned by :attr:`owner_user`.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The daemon instance for testing.
    """
    return baker.make(
        DaemonModel,
        log_filepath=faker.file_path(extension="log"),
        mailbox=mailboxModel,
    )


@pytest.fixture(name="daemonPayload")
def fixture_daemonPayload(faker, mailboxModel) -> dict[str, Any]:
    """Creates clean :class:`core.models.DaemonModel.DaemonModel` payload for a patch, post or put request.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The clean payload.
    """
    mailboxData = baker.prepare(
        DaemonModel,
        mailbox=mailboxModel,
        log_filepath=faker.file_path(extension="log"),
        cycle_interval=1234,
    )
    payload = model_to_dict(mailboxData)
    payload.pop("id")
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload


@pytest.mark.django_db
def test_list_noauth(daemonModel, noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(daemonModel, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(daemonModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(DaemonViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]


@pytest.mark.django_db
def test_get_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonModel.cycle_interval


@pytest.mark.django_db
def test_patch_noauth(daemonModel, noauth_apiClient, daemonPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_patch_auth_other(daemonModel, other_apiClient, daemonPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_patch_auth_owner(daemonModel, owner_apiClient, daemonPayload, detail_url):
    """Tests the patch method with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_apiClient.patch(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonPayload["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval == daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_noauth(daemonModel, noauth_apiClient, daemonPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_auth_other(daemonModel, other_apiClient, daemonPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval != daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_put_auth_owner(daemonModel, owner_apiClient, daemonPayload, detail_url):
    """Tests the put method with the authenticated owner user client.

    Note:
        Has a tendency to fail when not executed individually.
    """
    response = owner_apiClient.put(
        detail_url(DaemonViewSet, daemonModel), data=daemonPayload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["cycle_interval"] == daemonPayload["cycle_interval"]
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval == daemonPayload["cycle_interval"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, daemonPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, daemonPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, daemonPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(DaemonViewSet), data=daemonPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["cycle_interval"]
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(cycle_interval=daemonPayload["cycle_interval"])


@pytest.mark.django_db
def test_delete_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval is not None


@pytest.mark.django_db
def test_delete_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    daemonModel.refresh_from_db()
    assert daemonModel.cycle_interval is not None


@pytest.mark.django_db
def test_delete_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(DaemonViewSet, daemonModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(daemonModel.DoesNotExist):
        daemonModel.refresh_from_db()


@pytest.mark.django_db
def test_fetching_options_noauth(
    daemonModel, noauth_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with an unauthenticated user client."""
    mocker.patch(
        "core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria",
        return_value=["ALL"],
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_fetching_options_auth_other(
    daemonModel, other_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated other user client."""
    mocker.patch(
        "core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria",
        return_value=["ALL"],
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_fetching_options_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated owner user client."""
    mock_fetchingCriteria = ["ALL"]
    mocker.patch(
        "core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria",
        return_value=mock_fetchingCriteria,
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["options"] == mock_fetchingCriteria


@pytest.mark.django_db
def test_fetching_options_error_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.fetching_options` action with the authenticated owner user client."""
    mock_fetchingCriteria = []
    mocker.patch(
        "core.models.MailboxModel.MailboxModel.getAvailableFetchingCriteria",
        return_value=mock_fetchingCriteria,
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_FETCHING_OPTIONS, daemonModel
        )
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db
def test_test_noauth(daemonModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with an unauthenticated user client."""
    mock_testDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.testDaemon",
        return_value=True,
    )

    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["daemon"]
    mock_testDaemon.assert_not_called()


@pytest.mark.django_db
def test_test_auth_other(
    daemonModel, other_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated other user client."""
    mock_testDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.testDaemon",
        return_value=True,
    )

    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["daemon"]
    mock_testDaemon.assert_not_called()


@pytest.mark.django_db
def test_test_success_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""
    mock_testDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.testDaemon",
        return_value=True,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    assert response.data["result"] is True
    mock_testDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_test_failure_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.test` action with the authenticated owner user client."""
    mock_testDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.testDaemon",
        return_value=False,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_TEST, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    assert response.data["result"] is False
    mock_testDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_start_noauth(daemonModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with an unauthenticated user client."""
    mock_startDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.startDaemon",
        return_value=True,
    )

    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_startDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_start_auth_other(
    daemonModel, other_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated other user client."""
    mock_startDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.startDaemon",
        return_value=True,
    )

    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_startDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_start_success_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""
    mock_startDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.startDaemon",
        return_value=True,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_startDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_start_failure_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.start` action with the authenticated owner user client."""
    mock_startDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.startDaemon",
        return_value=False,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_START, daemonModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_startDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_stop_noauth(daemonModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with an unauthenticated user client."""
    mock_stopDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.stopDaemon",
        return_value=True,
    )

    response = noauth_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_stopDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_stop_auth_other(
    daemonModel, other_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated other user client."""
    mock_stopDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.stopDaemon",
        return_value=True,
    )

    response = other_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_stopDaemon.assert_not_called()
    with pytest.raises(KeyError):
        response.data["daemon"]


@pytest.mark.django_db
def test_stop_success_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    mock_stopDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.stopDaemon",
        return_value=True,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_stopDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_stop_failure_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the post method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.stop` action with the authenticated owner user client."""
    mock_stopDaemon = mocker.patch(
        "api.v1.views.DaemonViewSet.EMailArchiverDaemonRegistry.stopDaemon",
        return_value=False,
    )

    response = owner_apiClient.post(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_STOP, daemonModel
        )
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["daemon"] == DaemonViewSet.serializer_class(daemonModel).data
    mock_stopDaemon.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_download_noauth(
    daemonModel, noauth_apiClient, custom_detail_action_url, mocker
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with an unauthenticated user client."""
    mock_open = mocker.patch("api.v1.views.DaemonViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists", return_value=True
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    daemonModel, other_apiClient, custom_detail_action_url, mocker
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated other user client."""
    mock_open = mocker.patch("api.v1.views.DaemonViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists", return_value=True
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    mock_open = mocker.patch("api.v1.views.DaemonViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists", return_value=False
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(daemonModel.log_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    daemonModel, owner_apiClient, custom_detail_action_url, mocker
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.DaemonViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists", return_value=True
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(daemonModel.log_filepath)
    mock_open.assert_called_once_with(daemonModel.log_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(daemonModel.log_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
@pytest.mark.parametrize(
    "number_query_param, expected_suffix", [("1", ".1"), ("0", ""), ("abc", "")]
)
def test_download_auth_owner_numberquery(
    daemonModel,
    owner_apiClient,
    custom_detail_action_url,
    mocker,
    number_query_param,
    expected_suffix,
):
    """Tests the get method :func:`api.v1.views.DaemonViewSet.DaemonViewSet.log_download` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.DaemonViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.DaemonViewSet.os.path.exists", return_value=True
    )
    expected_log_filepath = daemonModel.log_filepath + expected_suffix

    response = owner_apiClient.get(
        custom_detail_action_url(
            DaemonViewSet, DaemonViewSet.URL_NAME_LOG_DOWNLOAD, daemonModel
        ),
        {"number": number_query_param},
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(expected_log_filepath)
    mock_open.assert_called_once_with(expected_log_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(expected_log_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent
