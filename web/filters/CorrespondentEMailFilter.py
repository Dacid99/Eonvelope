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

"""Module with the :class:`EMailFilter` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.db.models import Q
from django.forms import widgets

from core.constants import HeaderFields


if TYPE_CHECKING:
    from django.db.models import QuerySet


class EMailFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.EMailModel`."""

    search = django_filters.CharFilter(
        method="filter_text_fields",
        label="Search",
        widget=widgets.SearchInput,
    )
    datasize = django_filters.NumericRangeFilter(
        field_name="email__datasize",
        lookup_expr="range",
    )
    is_favorite = django_filters.BooleanFilter(
        field_name="email__is_favorite",
        widget=widgets.NullBooleanSelect,
    )
    mention = django_filters.MultipleChoiceFilter(
        field_name="mention",
        choices=HeaderFields.Correspondents.choices,
    )
    datetime__date__lt = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__lte",
        widget=widgets.SelectDateWidget,
    )
    datetime__date__gt = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__gt",
        widget=widgets.SelectDateWidget,
    )
    x_spam = django_filters.AllValuesMultipleFilter(
        field_name="email__x_spam",
    )

    o = django_filters.OrderingFilter(
        fields=[
            "email__message_id",
            "email__email_subject",
            "email__datetime",
            "mention",
            "email__datasize",
            "email__created",
            "email__updated",
        ]
    )

    def filter_text_fields(self, queryset: QuerySet, name: str, value: str) -> QuerySet:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        if value:
            return queryset.filter(
                Q(message_id__icontains=value)
                | Q(email_subject__icontains=value)
                | Q(plain_bodytext__icontains=value)
                | Q(html_bodytext__icontains=value)
                | Q(headers__has_key=value)
                | Q(correspondents__email_address=value)
            )
        return queryset
