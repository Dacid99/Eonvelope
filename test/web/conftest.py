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

"""File with fixtures required for all viewset tests. Automatically imported to `test_` files.

The viewset tests are made against a mocked consistent database with an instance of every model in every testcase.
"""

from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.fixture
def other_client(client, other_user):
    """A :class:`django.test.client.Client` instance that is authenticated as :attr:`other_user`."""
    client.force_login(user=other_user)
    return client


@pytest.fixture
def owner_client(client, owner_user):
    """A :class:`django.test.client.Client` instance that is authenticated as :attr:`owner_user`."""
    client.force_login(user=owner_user)
    return client


@pytest.fixture(scope="package")
def list_url():
    """Callable getting the viewsets url for list actions."""
    return lambda view_class: reverse(f"web:{view_class.URL_NAME}")


@pytest.fixture(scope="package")
def detail_url():
    """Callable getting the viewsets url for detail actions."""
    return lambda view_class, instance: reverse(
        f"web:{view_class.URL_NAME}", args=[instance.id]
    )


@pytest.fixture(scope="package")
def custom_list_action_url():
    """Callable getting the viewsets url for custom list actions."""
    return lambda view_class, custom_list_action_url_name: (
        reverse(f"web:{view_class.URL_NAME}-{custom_list_action_url_name}")
    )


@pytest.fixture(scope="package")
def custom_detail_action_url():
    """Callable getting the viewsets url for custom detail actions."""
    return lambda view_class, custom_detail_action_url_name, instance: (
        reverse(
            f"web:{view_class.URL_NAME}-{custom_detail_action_url_name}",
            args=[instance.id],
        )
    )
