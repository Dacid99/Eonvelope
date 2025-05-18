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


@pytest.fixture(autouse=True)
def complete_database(
    owner_user,
    other_user,
    fake_account,
    fake_attachment,
    fake_correspondent,
    fake_daemon,
    fake_email,
    fake_emailcorrespondent,
    fake_mailbox,
    fake_mailing_list,
):
    """Fixture providing a complete database setup."""


@pytest.fixture
def noauth_api_client() -> APIClient:
    """Fixture creating an unauthenticated :class:`rest_framework.test.APIClient` instance.

    Returns:
        The unauthenticated APIClient.
    """
    return APIClient()


@pytest.fixture
def other_api_client(noauth_api_client, other_user) -> APIClient:
    """Fixture creating a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`other_user`.

    Args:
        noauth_api_client: Depends on :func:`fixture_noauth_api_client`.
        other_user: Depends on :func:`fixture_other_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_api_client.force_authenticate(user=other_user)
    return noauth_api_client


@pytest.fixture
def owner_api_client(noauth_api_client, owner_user) -> APIClient:
    """Fixture creating a :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`owner_user`.

    Args:
        noauth_api_client: Depends on :func:`fixture_noauth_api_client`.
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_api_client.force_authenticate(user=owner_user)
    return noauth_api_client


@pytest.fixture(scope="package")
def list_url() -> Callable[[type[ModelViewSet]], str]:
    """Fixture getting the viewsets url for list actions.

    Returns:
        The list url.
    """
    return lambda viewset_class: reverse(f"api:v1:{viewset_class.BASENAME}-list")


@pytest.fixture(scope="package")
def detail_url() -> Callable[[type[ModelViewSet], Model], str]:
    """Fixture getting the viewsets url for detail actions.

    Returns:
        The detail url.
    """
    return lambda viewset_class, instance: reverse(
        f"api:v1:{viewset_class.BASENAME}-detail", args=[instance.id]
    )


@pytest.fixture(scope="package")
def custom_list_action_url() -> Callable[[type[ModelViewSet], str], str]:
    """Fixture getting the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda viewset_class, custom_list_action_url_name: (
        reverse(f"api:v1:{viewset_class.BASENAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="package")
def custom_detail_action_url() -> Callable[[type[ModelViewSet], str, Model], str]:
    """Fixture getting the viewsets url for custom detail actions.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda viewset_class, custom_detail_action_url_name, instance: (
        reverse(
            f"api:v1:{viewset_class.BASENAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )


@pytest.fixture(autouse=True)
def mock_os_remove(mocker):
    """Patches os.remove to prevent errors."""
    return mocker.patch("os.remove", autospec=True)
