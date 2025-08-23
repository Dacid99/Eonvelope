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

"""File with fixtures and configurations required for :mod:`test.core` tests. Automatically imported to `test_` files."""

from __future__ import annotations

from email.message import EmailMessage

import pytest


@pytest.fixture
def mock_message(mocker):
    """Fixture providing a mock :class:`email.message.EmailMessage` instance.

    Returns:
        :class:`unittest.mock.MagicMock`: The mock :class:`email.message.EmailMessage`.
    """
    return mocker.MagicMock(spec=EmailMessage)
