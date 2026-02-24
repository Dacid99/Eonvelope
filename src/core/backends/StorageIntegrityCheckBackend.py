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

"""Module with the :class:`core.backends.StorageIntegrityCheckBackend.StorageIntegrityCheckBackend` class."""

from asyncio import to_thread
from dataclasses import dataclass

from health_check import HealthCheck
from health_check.exceptions import ServiceWarning

from core.models import StorageShard


@dataclass
class StorageIntegrityCheckBackend(HealthCheck):
    """Health check backend for :func:`core.models.StorageShard.StorageShard.healthcheck`."""

    async def run(self) -> None:
        """Implements the healthcheck.

        Raises:
            ServiceWarning: If :func:`core.models.StorageShard.StorageShard.healthcheck` fails.
        """
        health = await to_thread(StorageShard.healthcheck)
        if not health:
            raise ServiceWarning(
                "The storage integrity is compromised, check the logs for critical level errors!"
            )
