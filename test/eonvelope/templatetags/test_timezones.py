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

"""Test module for the additional timezones tags."""

import zoneinfo

import pytest
from django.template import Context, Template, TemplateSyntaxError


def test_get_available_timezones_tag():
    """Tests the :func:`eonvelope.templatetags.get_available_timezones`."""
    template_str = "{% load timezones %}{% get_available_timezones as TIMEZONES %}"
    template = Template(template_str)
    context = Context({})

    template.render(context)

    assert "TIMEZONES" in context
    assert context["TIMEZONES"] == sorted(zoneinfo.available_timezones())


def test_get_available_timezones_tag_syntax_error():
    """Tests the :func:`eonvelope.templatetags.get_available_timezones`
    in case of a syntax error in the template.
    """
    bad_template_str = "{% load timezones %}{% get_available_timezones TIMEZONES %}"

    with pytest.raises(TemplateSyntaxError):
        Template(bad_template_str)
