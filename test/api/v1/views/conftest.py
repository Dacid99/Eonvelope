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
from django.urls import reverse
from rest_framework.test import APIClient


if TYPE_CHECKING:
    from collections.abc import Callable

    from django.db.models import Model
    from rest_framework.viewsets import ModelViewSet


@pytest.fixture
def noauth_apiClient() -> APIClient:
    """Creates an unauthenticated :class:`rest_framework.test.APIClient` instance.

    Returns:
        The unauthenticated APIClient.
    """
    return APIClient()


@pytest.fixture
def other_apiClient(noauth_apiClient, other_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`other_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        other_user: Depends on :func:`fixture_other_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=other_user)
    return noauth_apiClient


@pytest.fixture
def owner_apiClient(noauth_apiClient, owner_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`owner_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=owner_user)
    return noauth_apiClient


@pytest.fixture(scope="session")
def list_url() -> Callable[[type[ModelViewSet]], str]:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda viewsetClass: reverse(f"{viewsetClass.BASENAME}-list")


@pytest.fixture(scope="session")
def detail_url() -> Callable[[type[ModelViewSet], Model], str]:
    """Gets the viewsets url for detail actions.

    Returns:
        The detail url.
    """
    return lambda viewsetClass, instance: reverse(
        f"{viewsetClass.BASENAME}-detail", args=[instance.id]
    )


@pytest.fixture(scope="session")
def custom_list_action_url() -> Callable[[type[ModelViewSet], str], str]:
    """Gets the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda viewsetClass, custom_list_action_url_name: (
        reverse(f"{viewsetClass.BASENAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="session")
def custom_detail_action_url() -> Callable[[type[ModelViewSet], str, Model], str]:
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


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    """Patches os.remove to prevent errors."""
    return mocker.patch("os.remove", autospec=True)
