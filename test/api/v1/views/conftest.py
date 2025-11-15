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
):
    """Use a complete database setup for all view tests."""


@pytest.fixture
def url():
    """Callable getting the viewsets url for list actions."""
    return lambda view_class: reverse(f"api:v1:{view_class.NAME}")
