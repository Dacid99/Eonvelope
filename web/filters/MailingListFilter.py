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

"""Module with the :class:`MailingListFilter` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.db.models import Q
from django.forms import widgets

from ..utils.widgets import AdaptedSelectDateWidget


if TYPE_CHECKING:
    from django.db.models import QuerySet


class MailingListFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.MailingListModel`."""

    order = django_filters.OrderingFilter(
        fields=[
            "list_id",
            "list_owner",
            "list_subscribe",
            "list_unsubscribe",
            "list_post",
            "list_help",
            "list_archive",
            "created",
        ]
    )

    text_search = django_filters.CharFilter(
        method="filter_text_fields",
        label="Search",
        widget=widgets.SearchInput,
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
    is_favorite = django_filters.BooleanFilter(
        field_name="is_favorite",
        widget=widgets.NullBooleanSelect,
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
                Q(list_id__icontains=value)
                | Q(list_owner__icontains=value)
                | Q(list_subscribe__icontains=value)
                | Q(list_unsubscribe__icontains=value)
                | Q(list_post__icontains=value)
                | Q(list_help__icontains=value)
                | Q(list_archive__icontains=value)
            ).distinct()
        return queryset
