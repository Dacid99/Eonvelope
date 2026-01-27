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

"""Module with the :class:`TimezoneMiddleware`."""

from __future__ import annotations

import logging
import zoneinfo
from typing import TYPE_CHECKING

from django.utils import timezone

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http.request import HttpRequest
    from django.http.response import HttpResponse


logger = logging.getLogger(__name__)


class TimezoneMiddleware:
    """Middleware to enable the chosen timezone for the request.

    References:
        https://docs.djangoproject.com/en/5.2/topics/i18n/timezones/#selecting-the-current-time-zone
    """

    TIMEZONE_SESSION_KEY = "django_timezone"

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Sets up the middleware."""
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Activates the timezone from the requests session.

        Args:
            request: The request to handle.

        Returns:
            The response to the request.
        """
        tzname = request.session.get(self.TIMEZONE_SESSION_KEY)
        try:
            timezone.activate(
                zoneinfo.ZoneInfo(tzname) if tzname else timezone.get_default_timezone()
            )
        except zoneinfo.ZoneInfoNotFoundError:
            timezone.activate(timezone.get_default_timezone())
            logger.warning("Timezone %s not found, using default timezone.", tzname)
        return self.get_response(request)
