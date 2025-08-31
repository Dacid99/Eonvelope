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

"""Test module for the :class:`DBReconnectMiddleware`."""

import pytest
from django.conf import settings
from django.db import OperationalError, connection

from test.web.conftest import owner_client


@pytest.fixture
def mock_time_sleep(mocker):
    """Patches :func:`time.sleep` to not waste time."""
    return mocker.patch("Emailkasten.middleware.DBReconnectMiddleware.time.sleep")


@pytest.mark.django_db
def test_reconnect(monkeypatch, owner_client, mock_time_sleep):
    """Tests reconnection to the db by :class:`Emailkasten.middleware.DBReconnectMiddleware`."""
    monkeypatch.setattr(
        connection,
        "cursor",
        lambda: (_ for _ in ()).throw(OperationalError()),
    )

    with pytest.raises(OperationalError):
        owner_client.get("/")

    assert mock_time_sleep.call_count == settings.DATABASE_RECONNECT_RETRIES
    mock_time_sleep.assert_called_with(settings.DATABASE_RECONNECT_DELAY)
