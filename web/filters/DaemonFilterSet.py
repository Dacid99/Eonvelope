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

"""Module with the :class:`DaemonFilterSet` filter set class."""

from __future__ import annotations

import django_filters
from django.forms import widgets

from core.constants import EmailFetchingCriterionChoices

from ..utils.widgets import AdaptedSelectDateWidget


class DaemonFilterSet(django_filters.FilterSet):
    """The filter class for :class:`core.models.Mailbox.Mailbox`."""

    order = django_filters.OrderingFilter(
        fields=[
            "uuid",
            "cycle_interval",
            "created",
            "updated",
        ]
    )

    fetching_criterion = django_filters.MultipleChoiceFilter(
        choices=EmailFetchingCriterionChoices.choices,
        widget=widgets.CheckboxSelectMultiple,
    )
    cycle_interval = django_filters.RangeFilter(
        field_name="cycle_interval",
        lookup_expr="range",
    )
    created__date__lte = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__lte",
        label="Created before",
        widget=AdaptedSelectDateWidget,
    )
    created__date__gte = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__gte",
        label="Created after",
        widget=AdaptedSelectDateWidget,
    )
    is_running = django_filters.BooleanFilter(
        field_name="is_running",
        widget=widgets.NullBooleanSelect,
    )
    is_healthy = django_filters.BooleanFilter(
        field_name="is_healthy",
        widget=widgets.NullBooleanSelect,
    )
