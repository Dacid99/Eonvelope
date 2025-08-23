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

"""Module with the :class:`core.backends.StorageIntegrityCheckBackend.StorageIntegrityCheckBackend` class."""

from health_check.backends import BaseHealthCheckBackend, HealthCheckException

from ..models import StorageShard


class StorageIntegrityCheckBackend(BaseHealthCheckBackend):
    """Health check backend for :func:`core.models.StorageShard.StorageShard.healthcheck`."""

    critical_service = False

    def check_status(self) -> None:
        """Implements the healthcheck.

        Raises:
            HealthCheckException: If :func:`core.models.StorageShard.StorageShard.healthcheck` fails.
        """
        if not StorageShard.healthcheck():
            raise HealthCheckException(
                "The storage integrity is compromised, check the logs for critical level errors!"
            )
