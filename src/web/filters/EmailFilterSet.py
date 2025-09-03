# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with the :class:`EmailFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.db.models import Q
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from web.utils.widgets import AdaptedSelectDateWidget


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import Email


class EmailFilterSet(django_filters.FilterSet):
    """The filter class for :class:`core.models.Email`."""

    order = django_filters.OrderingFilter(
        fields=[
            "subject",
            "datetime",
            "datasize",
            "created",
        ]
    )

    search = django_filters.CharFilter(
        method="filter_text_fields",
        label=_("Search"),
        widget=widgets.SearchInput,
    )
    datasize = django_filters.RangeFilter(
        field_name="datasize",
        lookup_expr="range",
    )
    is_favorite = django_filters.BooleanFilter(
        field_name="is_favorite",
        widget=widgets.NullBooleanSelect,
    )
    datetime__date__lte = django_filters.DateTimeFilter(
        field_name="datetime",
        lookup_expr="date__lte",
        label=_("Received before"),
        widget=AdaptedSelectDateWidget,
    )
    datetime__date__gte = django_filters.DateTimeFilter(
        field_name="datetime",
        lookup_expr="date__gte",
        label=_("Received after"),
        widget=AdaptedSelectDateWidget,
    )
    x_spam = django_filters.AllValuesMultipleFilter(
        field_name="x_spam",
    )

    def filter_text_fields(
        self, queryset: QuerySet[Email], name: str, value: str
    ) -> QuerySet[Email]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(message_id__icontains=value)
            | Q(subject__icontains=value)
            | Q(plain_bodytext__icontains=value)
            | Q(html_bodytext__icontains=value)
            | Q(headers__has_any_keys=value)
            | Q(correspondents__email_address__icontains=value)
            | Q(attachments__file_name__icontains=value)
        ).distinct()
