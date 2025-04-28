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

"""Test module for the :class:`core.backends.StorageIntegrityCheckBackend.StorageIntegrityCheckBackend` class."""

import pytest
from health_check.backends import HealthCheckException

from core.backends.StorageIntegrityCheckBackend import StorageIntegrityCheckBackend


@pytest.fixture
def mock_StorageModel_healthcheck(mocker):
    return mocker.patch(
        "core.backends.StorageIntegrityCheckBackend.StorageModel.healthcheck"
    )


def test_StorageIntegrityCheckBackend_check_status_success(
    mock_StorageModel_healthcheck,
):
    """Test the healthcheck for the storage if it is healthy."""
    mock_StorageModel_healthcheck.return_value = True

    StorageIntegrityCheckBackend().check_status()


def test_StorageIntegrityCheckBackend_check_status_failure(
    mock_StorageModel_healthcheck,
):
    """Test the healthcheck for the storage if it is not healthy."""
    mock_StorageModel_healthcheck.return_value = False

    with pytest.raises(HealthCheckException):
        StorageIntegrityCheckBackend().check_status()
