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

"""File with fixtures required for all viewset tests. Automatically imported to test_ files.

The viewset tests are made against a mocked consistent database with an instance of every model in every testcase.

Fixtures:
    :func:`fixture_owner_user`: Creates a user that represents the owner of the data.
    :func:`fixture_other_user`: Creates a user that represents another user that is not the owner of the data.
    :func:`fixture_noauth_apiClient`: Creates an unauthenticated :class:`rest_framework.test.APIClient` instance.
    :func:`fixture_auth_other_apiClient`: Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as `other_user`.
    :func:`fixture_auth_owner_apiClient`: Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as `owner_user`.
    :func:`fixture_list_url`: Gets the viewsets url for list actions.
    :func:`fixture_detail_url`: Gets the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Gets the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Gets the viewsets url for custom detail actions.
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_mailboxModel`: Creates an mailbox in `accountModel`.
    :func:`fixture_correspondentModel`: Creates an email in `accountModel`.
    :func:`fixture_mailingListModel`: Creates an email in `accountModel`.
    :func:`fixture_attachmentModel`: Creates an attachment in `emailModel`.
    :func:`fixture_emailModel`: Creates an email in `accountModel`.
    :func:`fixture_daemonModel`: Creates an mailbox in `accountModel`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import Model
    from rest_framework.viewsets import ModelViewSet


@pytest.fixture(name="owner_user", autouse=True)
def fixture_owner_user() -> User:
    """Creates a :class:`django.contrib.auth.models.User` that owns the data.

    Returns:
        The owner user instance.
    """
    return baker.make(User)


@pytest.fixture(name="other_user", autouse=True)
def fixture_other_user() -> User:
    """Creates a :class:`django.contrib.auth.models.User` that is not the owner of the data.

    Returns:
       The other user instance.
    """
    return baker.make(User)


@pytest.fixture(name="noauth_apiClient")
def fixture_noauth_apiClient() -> APIClient:
    """Creates an unauthenticated :class:`rest_framework.test.APIClient` instance.

    Returns:
        The unauthenticated APIClient.
    """
    return APIClient()


@pytest.fixture(name="other_apiClient")
def fixture_other_apiClient(noauth_apiClient, other_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`other_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        other_user: Depends on :func:`fixture_other_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=other_user)
    return noauth_apiClient


@pytest.fixture(name="owner_apiClient")
def fixture_owner_apiClient(noauth_apiClient, owner_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`owner_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=owner_user)
    return noauth_apiClient


@pytest.fixture(name="list_url")
def fixture_list_url() -> Callable[[type[ModelViewSet]], str]:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda viewsetClass: reverse(f"{viewsetClass.BASENAME}-list")


@pytest.fixture(name="detail_url")
def fixture_detail_url() -> Callable[[type[ModelViewSet], Model], str]:
    """Gets the viewsets url for detail actions.

    Returns:
        The detail url.
    """
    return lambda viewsetClass, instance: reverse(
        f"{viewsetClass.BASENAME}-detail", args=[instance.id]
    )


@pytest.fixture(name="custom_list_action_url")
def fixture_custom_list_action_url() -> Callable[[type[ModelViewSet], str], str]:
    """Gets the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda viewsetClass, custom_list_action_url_name: (
        reverse(f"{viewsetClass.BASENAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(name="custom_detail_action_url")
def fixture_custom_detail_action_url() -> (
    Callable[[type[ModelViewSet], str, Model], str]
):
    """Gets the viewsets url for custom detail actions.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda viewsetClass, custom_detail_action_url_name, instance: (
        reverse(
            f"{viewsetClass.BASENAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )


@pytest.fixture(name="mock_os_remove", autouse=True)
def fixture_mock_AttachmentModel_os_remove(mocker):
    """Patches os.remove in AttachmentModel to prevent errors."""
    return mocker.patch("core.models.AttachmentModel.os.remove", autospec=True)


@pytest.fixture(name="mock_os_remove", autouse=True)
def fixture_mock_EMailModel_os_remove(mocker):
    """Patches os.remove in EMailModel to prevent errors."""
    return mocker.patch("core.models.EMailModel.os.remove", autospec=True)


@pytest.fixture(name="accountModel", autouse=True)
def fixture_accountModel(owner_user) -> AccountModel:
    """Creates an :class:`core.models.AccountModel.AccountModel` owned by :attr:`owner_user`.

    Args:
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel, user=owner_user)


@pytest.fixture(name="mailboxModel", autouse=True)
def fixture_mailboxModel(accountModel) -> MailboxModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel` owned by :attr:`owner_user`.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The mailbox instance for testing.
    """
    return baker.make(MailboxModel, account=accountModel)


@pytest.fixture(name="daemonModel", autouse=True)
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


@pytest.fixture(name="correspondentModel", autouse=True)
def fixture_correspondentModel() -> CorrespondentModel:
    """Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` owned by :attr:`owner_user`.

    Returns:
        The correspondent instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.fixture(name="mailingListModel", autouse=True)
def fixture_mailingListModel() -> MailingListModel:
    """Creates an :class:`core.models.MailingListModel.MailingListModel` owned by :attr:`owner_user`.

    Returns:
        The mailinglist instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.fixture(name="emailModel", autouse=True)
def fixture_emailModel(
    faker, correspondentModel, mailboxModel, mailingListModel
) -> EMailModel:
    """Creates an :class:`core.models.EMailModel.EMailModel` owned by :attr:`owner_user`.

    Args:
        mailboxcorrespondentModelModel: Depends on :func:`fixture_correspondentModel`.
        mailboxModel: Depends on :func:`fixture_mailboxModel`.
        mailinglistModel: Depends on :func:`fixture_mailinglistModel`.

    Returns:
        The email instance for testing.
    """
    emailModel = baker.make(
        EMailModel,
        mailbox=mailboxModel,
        mailinglist=mailingListModel,
        eml_filepath=faker.file_path(extension="eml"),
        prerender_filepath=faker.file_path(extension="png"),
    )
    baker.make(
        EMailCorrespondentsModel, email=emailModel, correspondent=correspondentModel
    )
    return emailModel


@pytest.fixture(name="attachmentModel", autouse=True)
def fixture_attachmentModel(faker, emailModel) -> AttachmentModel:
    """Creates an :class:`core.models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Args:
        emailModel: Depends on :func:`fixture_emailModel`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(
        AttachmentModel, email=emailModel, file_path=faker.file_path(extension="pdf")
    )
