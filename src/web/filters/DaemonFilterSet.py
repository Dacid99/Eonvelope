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
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import IntervalSchedule

from core.constants import EmailFetchingCriterionChoices

from ..utils.widgets import AdaptedSelectDateWidget


class DaemonFilterSet(django_filters.FilterSet):
    """The filter class for :class:`core.models.Mailbox`."""

    order = django_filters.OrderingFilter(
        fields=[
            "uuid",
            "interval__every",
            "interval__period",
            "celery_task__last_run_at",
            "celery_task__total_run_count",
            "created",
            "updated",
        ]
    )

    fetching_criterion = django_filters.MultipleChoiceFilter(
        choices=EmailFetchingCriterionChoices.choices,
        widget=widgets.CheckboxSelectMultiple,
    )
    interval__every = django_filters.RangeFilter(
        field_name="interval__every",
        lookup_expr="range",
        label=_("Number of intervals"),
    )
    interval__period = django_filters.MultipleChoiceFilter(
        field_name="interval__period",
        choices=IntervalSchedule.PERIOD_CHOICES,
        widget=widgets.CheckboxSelectMultiple,
        label=_("Interval period"),
    )
    celery_task__enabled = django_filters.BooleanFilter(
        field_name="celery_task__enabled",
        widget=widgets.NullBooleanSelect,
        label=_("Enabled"),
    )
    created__date__lte = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__lte",
        label=_("Created before"),
        widget=AdaptedSelectDateWidget,
    )
    created__date__gte = django_filters.DateTimeFilter(
        field_name="created",
        lookup_expr="date__gte",
        label=_("Created after"),
        widget=AdaptedSelectDateWidget,
    )
    is_healthy = django_filters.BooleanFilter(
        field_name="is_healthy",
        widget=widgets.NullBooleanSelect,
    )
