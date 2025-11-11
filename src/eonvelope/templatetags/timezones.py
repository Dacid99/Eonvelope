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

"""Module with templatestags for timezone."""

import zoneinfo
from typing import Any, Literal, override

from django.template import Context, Library, Node, TemplateSyntaxError


register = Library()


class GetAvailableTimezonesNode(Node):
    """Node putting the output of :func:`zoneinfo.available_timezones` in the context.

    Note:
        Analogous to :func:`django.templatetags.i18n.GetAvailableTimezonesNode`.
    """

    def __init__(self, variable: Any) -> None:
        """Constructor for the node."""
        self.variable = variable

    @override
    def render(self, context: Context) -> Literal[""]:
        """Adds available timezones to the context.

        Args:
            context: The template context.

        Returns:
            The empty string
        """
        context[self.variable] = sorted(zoneinfo.available_timezones())
        return ""


@register.tag("get_available_timezones")
def do_get_available_timezones(parser, token) -> GetAvailableTimezonesNode:
    """Store a list of available timezones in the context.

    Usage::

        {% get_available_timezones as timezones %}
        {% for timezone in timezones %}
        ...
        {% endfor %}

    This puts zoneinfo.available_timezones() into the named variable.

    Note:
        Analogous to :func:`django.templatetags.i18n.do_get_available_languages`.
    """
    # token.split_contents() isn't useful here because this tag doesn't accept
    # variable as arguments.
    args = token.contents.split()
    if len(args) != 3 or args[1] != "as":  # noqa: PLR2004 ; just checking for length
        # pylint: disable=consider-using-f-string  # does not need to be evaluated early
        raise TemplateSyntaxError(
            "'get_available_timezones' requires 'as variable' (got %r)"  # noqa: UP031
            % args
        )
    return GetAvailableTimezonesNode(args[2])
