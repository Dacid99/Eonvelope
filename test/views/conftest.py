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

"""File with fixtures required for all viewset tests. Automatically imported to test_ files."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

if TYPE_CHECKING:
    from typing import Callable


@pytest.fixture(name='owner_user')
def fixture_owner_user() -> User:
    """Creates a :class:`django.contrib.auth.models.User`
    that represents the owner of the data.
    Invoked as owner_user.

    Returns:
        The owner user instance.
    """
    return baker.make(User)

@pytest.fixture(name='other_user')
def fixture_other_user() -> User:
    """Creates a :class:`django.contrib.auth.models.User`
    that represents another user that is not the owner of the data.
    Invoked as other_user.

    Returns:
       The other user instance.
    """
    return baker.make(User)


@pytest.fixture(name='noauth_apiClient')
def fixture_noauth_apiClient() -> APIClient:
    """Creates an unauthenticated :class:`rest_framework.test.APIClient` instance.

    Returns:
        The unauthenticated APIClient.
    """
    return APIClient()


@pytest.fixture(name='other_apiClient')
def fixture_other_apiClient(noauth_apiClient, other_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance
    that is authenticated as :attr:`other_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        other_user: Depends on :func:`fixture_other_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=other_user)
    return noauth_apiClient

@pytest.fixture(name='owner_apiClient')
def fixture_owner_apiClient(noauth_apiClient, owner_user) -> APIClient:
    """Creates a :class:`rest_framework.test.APIClient` instance
    that is authenticated as :attr:`owner_user`.

    Args:
        noauth_apiClient: Depends on :func:`fixture_noauth_apiClient`.
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The authenticated APIClient.
    """
    noauth_apiClient.force_authenticate(user=owner_user)
    return noauth_apiClient
