# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""File with fixtures required for all viewset tests. Automatically imported to `test_` files.

The viewset tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def noauth_api_client() -> APIClient:
    """An unauthenticated :class:`rest_framework.test.APIClient` instance."""
    return APIClient()


@pytest.fixture
def other_api_client(noauth_api_client, other_user) -> APIClient:
    """A :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`other_user`."""
    noauth_api_client.force_authenticate(user=other_user)
    return noauth_api_client


@pytest.fixture
def owner_api_client(noauth_api_client, owner_user) -> APIClient:
    """A :class:`rest_framework.test.APIClient` instance that is authenticated as :attr:`owner_user`."""
    noauth_api_client.force_authenticate(user=owner_user)
    return noauth_api_client
