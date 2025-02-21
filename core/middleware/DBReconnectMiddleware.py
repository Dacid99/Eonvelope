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

"""Module with the custom :class:`DBReconnectMiddleware`."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from django.db import OperationalError, connection

from Emailkasten.constants import DatabaseConfiguration


if TYPE_CHECKING:
    from collections.abc import Callable

    from rest_framework.request import Request
    from rest_framework.response import Response


class DBReconnectMiddleware:
    """Middleware to reconnect to the database.

    Elementary for initial setup.
    """

    max_retries = DatabaseConfiguration.RECONNECT_RETRIES
    """The number of times to retry connecting.
    Set from :attr:`Emailkasten.constants.DatabaseConfiguration.RECONNECT_RETRIES`."""

    delay = DatabaseConfiguration.RECONNECT_DELAY
    """The time delay between reconnect attempt.
    Set from :attr:`Emailkasten.constants.DatabaseConfiguration.RECONNECT_DELAY`."""

    def __init__(self, get_response: Callable):
        """Sets up the middleware."""
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        """Attempts to connect to the database :attr:`max_retries` times.

        Args:
            request: The request to handle.

        Raises:
            :class:`django.db.OperationalError`: If no connection attempt is successful.

        Returns:
            The response to the request.
        """
        for attempt in range(self.max_retries):
            try:
                with connection.cursor():
                    break
            except OperationalError:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(self.delay)

        return self.get_response(request)
