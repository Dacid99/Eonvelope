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
    :func:`fixture_noauth_client`: Fixture creating an unauthenticated :class:`rest_framework.test.Client` instance.
    :func:`fixture_auth_other_client`: Fixture creating a :class:`rest_framework.test.Client` instance that is authenticated as `other_user`.
    :func:`fixture_auth_owner_client`: Fixture creating a :class:`rest_framework.test.Client` instance that is authenticated as `owner_user`.
    :func:`fixture_list_url`: Fixture getting the viewsets url for list actions.
    :func:`fixture_detail_url`: Fixture getting the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Fixture getting the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Fixture getting the viewsets url for custom detail actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse


if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import Model
    from django.test.client import Client
    from rest_framework.viewsets import ModelViewSet


@pytest.fixture(autouse=True)
def complete_database(
    owner_user,
    other_user,
    accountModel,
    attachmentModel,
    correspondentModel,
    daemonModel,
    emailModel,
    mailboxModel,
    mailingListModel,
):
    """Fixture providing a complete database setup."""


@pytest.fixture
def other_client(client, other_user) -> Client:
    """Fixture creating a :class:`django.test.client.Client` instance that is authenticated as :attr:`other_user`.

    Returns:
        The authenticated Client.
    """
    client.force_login(user=other_user)
    return client


@pytest.fixture
def owner_client(client, owner_user) -> Client:
    """Fixture creating a :class:`django.test.client.Client` instance that is authenticated as :attr:`owner_user`.

    Returns:
        The authenticated Client.
    """
    client.force_login(user=owner_user)
    return client


@pytest.fixture(scope="package")
def login_url() -> str:
    """Fixture with the login url.

    Returns:
        The login url.
    """
    return reverse("account_login")


@pytest.fixture(scope="package")
def list_url() -> Callable[[type[ModelViewSet]], str]:
    """Fixture getting the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda viewClass: reverse(f"web:{viewClass.URL_NAME}")


@pytest.fixture(scope="package")
def detail_url() -> Callable[[type[ModelViewSet], Model], str]:
    """Fixture getting the viewsets url for detail actions.

    Returns:
        The detail url.
    """
    return lambda viewClass, instance: reverse(
        f"web:{viewClass.URL_NAME}", args=[instance.id]
    )


@pytest.fixture(scope="package")
def custom_list_action_url() -> Callable[[type[ModelViewSet], str], str]:
    """Fixture getting the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda viewClass, custom_list_action_url_name: (
        reverse(f"web:{viewClass.URL_NAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="package")
def custom_detail_action_url() -> Callable[[type[ModelViewSet], str, Model], str]:
    """Fixture getting the viewsets url for custom detail actions.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda viewClass, custom_detail_action_url_name, instance: (
        reverse(
            f"web:{viewClass.URL_NAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    """Patches :func:`os.remove` to prevent errors."""
    return mocker.patch("os.remove", autospec=True)


@pytest.fixture
def mock_AccountModel_test_connection(mocker):
    """Patches :func:`core.models.AccountModel.AccountModel.test_connection` for testing of the test action."""
    return mocker.patch(
        "core.models.AccountModel.AccountModel.test_connection",
        autospec=True,
    )


@pytest.fixture
def mock_AccountModel_update_mailboxes(mocker):
    """Patches :func:`core.models.AccountModel.AccountModel.update_mailboxes` for testing of the test action."""
    return mocker.patch(
        "core.models.AccountModel.AccountModel.update_mailboxes",
        autospec=True,
    )


@pytest.fixture
def mock_MailboxModel_test_connection(mocker):
    """Patches :func:`core.models.MailboxModel.MailboxModel.test_connection` for testing of the test action."""
    return mocker.patch(
        "core.models.MailboxModel.MailboxModel.test_connection",
        autospec=True,
    )


@pytest.fixture
def mock_MailboxModel_fetch(mocker):
    """Patches :func:`core.models.MailboxModel.MailboxModel.fetch` for testing of the test action."""
    return mocker.patch(
        "core.models.MailboxModel.MailboxModel.fetch",
        autospec=True,
    )


@pytest.fixture
def mock_EMailArchiverDaemonRegistry_startDaemon(mocker):
    """Patches :func:`core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.startDaemon` for testing of the start action."""
    return mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.startDaemon",
        autospec=True,
        return_value=True,
    )


@pytest.fixture
def mock_EMailArchiverDaemonRegistry_stopDaemon(mocker):
    """Patches :func:`core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.stopDaemon` for testing of the stop action."""
    return mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.stopDaemon",
        autospec=True,
        return_value=True,
    )
