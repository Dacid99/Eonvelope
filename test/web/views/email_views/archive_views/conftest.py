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

"""File with fixtures required for all archive views tests. Automatically imported to `test_` files."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.urls import reverse


if TYPE_CHECKING:
    from collections.abc import Callable

    from rest_framework.viewsets import ModelViewSet


@pytest.fixture(scope="package")
def date_url() -> Callable[[type[ModelViewSet]], str]:
    """Callable getting the view url for date based views."""
    return lambda view_class, date_args=[]: reverse(
        f"web:{view_class.URL_NAME}", args=date_args
    )
