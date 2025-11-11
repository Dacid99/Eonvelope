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

"""Module with views for working with timezones in Eonvelope project."""

import zoneinfo

from django.http import HttpResponse, HttpResponseRedirect
from django.http.request import HttpRequest
from django.utils.http import url_has_allowed_host_and_scheme

from eonvelope.middleware.TimezoneMiddleware import TimezoneMiddleware


TIMEZONE_FIELD_NAME = "timezone"

SET_TIMEZONE_URL_NAME = "set_timezone"


def set_timezone(request: HttpRequest) -> HttpResponse:
    """Redirect to a given URL while setting the chosen timezone in the session.

    The URL and the timezone code need to be
    specified in the request parameters.

    Since this view changes how the user will see the rest of the site, it must
    only be accessed as a POST request. If called as a GET request, it will
    redirect to the page in the request (the 'next' parameter) without changing
    any state.

    Note:
        Analogous to :func:`django.views.i18n.get_language`.
    """
    next_url = request.POST.get("next", request.GET.get("next"))
    if (
        next_url or request.accepts("text/html")
    ) and not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"
    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)
    if request.method == "POST":
        timezone_code = request.POST.get(TIMEZONE_FIELD_NAME)
        if timezone_code and check_for_timezone(timezone_code):
            request.session[TimezoneMiddleware.TIMEZONE_SESSION_KEY] = request.POST[
                TIMEZONE_FIELD_NAME
            ]
    return response


def check_for_timezone(timezone_code: str) -> bool:
    """Check the timezone code for validity and availability.

    Args:
        The code of the timezone.

    Returns:
        Whether the timezone code is valid and the tz data available.s
    """
    try:
        zoneinfo.ZoneInfo(timezone_code)
    except zoneinfo.ZoneInfoNotFoundError:
        return False
    else:
        return True
