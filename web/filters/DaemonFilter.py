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

"""Module with the :class:`DaemonFilter` filter set class."""

from __future__ import annotations

import django_filters
from django.forms import widgets

from core.constants import EmailFetchingCriterionChoices


class DaemonFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.MailboxModel`."""

    fetching_criterion = django_filters.MultipleChoiceFilter(
        choices=EmailFetchingCriterionChoices.choices
    )
    cycle_interval = django_filters.NumericRangeFilter(
        field_name="cycle_interval",
        lookup_expr="range",
    )
    created__date__lt = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__lte",
        widget=widgets.SelectDateWidget,
    )
    created__date__gt = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__gt",
        widget=widgets.SelectDateWidget,
    )
    is_running = django_filters.BooleanFilter(
        field_name="is_running",
        widget=widgets.NullBooleanSelect,
    )
    is_healthy = django_filters.BooleanFilter(
        field_name="is_healthy",
        widget=widgets.NullBooleanSelect,
    )

    o = django_filters.OrderingFilter(
        fields=[
            "uuid",
            "cycle_interval",
            "created",
            "updated",
        ]
    )
