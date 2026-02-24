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

"""Test module for the :class:`core.backends.StorageIntegrityCheckBackend.StorageIntegrityCheckBackend` class."""

import asyncio

import pytest
from health_check.exceptions import ServiceWarning

from core.backends import StorageIntegrityCheckBackend


@pytest.fixture
def mock_StorageShard_healthcheck(mocker):
    """Patches `core.models.StorageShard.healthcheck`."""
    return mocker.patch("core.models.StorageShard.StorageShard.healthcheck")


def test_StorageIntegrityCheckBackend_check_status__success(
    mock_StorageShard_healthcheck,
):
    """Test the healthcheck for the storage if it is healthy."""
    mock_StorageShard_healthcheck.return_value = True

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(StorageIntegrityCheckBackend().run())
    finally:
        loop.close()

    mock_StorageShard_healthcheck.assert_called_once()


def test_StorageIntegrityCheckBackend_check_status__failure(
    mock_StorageShard_healthcheck,
):
    """Test the healthcheck for the storage if it is not healthy."""
    mock_StorageShard_healthcheck.return_value = False

    loop = asyncio.new_event_loop()
    try:
        with pytest.raises(ServiceWarning):
            loop.run_until_complete(StorageIntegrityCheckBackend().run())
    finally:
        loop.close()

    mock_StorageShard_healthcheck.assert_called_once()
