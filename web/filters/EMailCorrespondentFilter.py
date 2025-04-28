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

"""Module with the :class:`CorrespondentFilter` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.db.models import Q
from django.forms import widgets

from core.constants import HeaderFields

from ..utils.widgets import AdaptedSelectDateWidget


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel


class EMailCorrespondentFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.CorrespondentModel`."""

    order = django_filters.OrderingFilter(
        fields=[
            "correspondent__email_name",
            "correspondent__email_address",
            "mention",
            "correspondent__created",
            "correspondent__updated",
        ]
    )

    text_search = django_filters.CharFilter(
        method="filter_text_fields",
        label="Search",
        widget=widgets.SearchInput,
    )
    mention = django_filters.MultipleChoiceFilter(
        field_name="mention",
        choices=HeaderFields.Correspondents.choices,
    )
    created__date__lte = django_filters.DateTimeFilter(
        field_name="correspondent__created",
        lookup_expr="date__lte",
        label="Created before",
        widget=AdaptedSelectDateWidget,
    )
    created__date__gte = django_filters.DateTimeFilter(
        field_name="correspondent__created",
        lookup_expr="date__gte",
        label="Created after",
        widget=AdaptedSelectDateWidget,
    )
    is_favorite = django_filters.BooleanFilter(
        field_name="correspondent__is_favorite",
        widget=widgets.NullBooleanSelect,
    )

    def filter_text_fields(
        self, queryset: QuerySet[EMailCorrespondentsModel], name: str, value: str
    ) -> QuerySet[EMailCorrespondentsModel]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(correspondent__email_address__icontains=value)
            | Q(correspondent__email_name__icontains=value)
        ).distinct()
