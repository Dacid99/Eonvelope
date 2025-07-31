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

"""Module with :class:`web.mixins.CustomActionMixin`."""

from typing import Final

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from rest_framework import status


class CustomActionMixin:
    """Mixin to provide action button handling for views.

    To register handlers for the different actions
    define a viewclass method `handle_action`
    that creates the appropriate response to a `action` post request.
    """

    _handler_method_prefix: Final[str] = "handle_"
    """The name prefix of methods considered request handlers."""

    def post(self, request: HttpRequest) -> HttpResponse:
        """Creates response to a post request.

        If no action matches the existing handlers, responds with Http204.
        Should be executed last in a custom view post method.

        Args:
            request: The post request to handle.

        Returns:
            The handlers response to the request.
            If no matching handler is found Http204.

        Raises:
           ImproperlyConfigured: If the called handler method does not return a :class:`django.http.HttpResponse`.>
        """
        for attr in dir(self):
            if (
                attr.startswith(self._handler_method_prefix)
                and attr.removeprefix(self._handler_method_prefix) in request.POST
            ):
                response = getattr(self, attr)(request)
                if isinstance(response, HttpResponse):
                    return response
                raise ImproperlyConfigured(
                    f"The custom action handler {attr} did not return a HttpResponse!"
                )
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
