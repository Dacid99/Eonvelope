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

"""Module with the :class:`AttachmentFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import django_filters
from django.db import models
from django.forms import widgets
from django.utils.translation import gettext_lazy as _

from web.utils.widgets import AdaptedSelectDateWidget

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from core.models import Attachment


class AttachmentFilterSet(django_filters.FilterSet):
    """The filter class for :class:`core.models.Attachment`."""

    order = django_filters.OrderingFilter(
        fields=[
            "file_name",
            "content_maintype",
            "content_subtype",
            "content_disposition",
            "datasize",
            "email__datetime",
            "created",
        ]
    )
    search = django_filters.CharFilter(
        method="filter_text_fields",
        label=_("Search"),
        widget=widgets.SearchInput,
    )
    content_maintype = django_filters.AllValuesMultipleFilter(
        field_name="content_maintype",
    )
    content_subtype = django_filters.AllValuesMultipleFilter(
        field_name="content_subtype",
    )
    content_disposition = django_filters.AllValuesMultipleFilter(
        field_name="content_disposition",
    )
    datasize = django_filters.RangeFilter(
        field_name="datasize",
        lookup_expr="range",
    )
    is_favorite = django_filters.BooleanFilter(
        field_name="is_favorite",
        widget=widgets.NullBooleanSelect,
    )
    email__datetime__date__lte = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__lte",
        label=_("Received before"),
        widget=AdaptedSelectDateWidget,
    )
    email__datetime__date__gte = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__gte",
        label=_("Received after"),
        widget=AdaptedSelectDateWidget,
    )

    def filter_text_fields(
        self, queryset: QuerySet[Attachment], name: str, value: str
    ) -> QuerySet[Attachment]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            models.Q(file_name__icontains=value)
            | models.Q(content_id__icontains=value)
            | models.Q(email__subject__icontains=value)
            | models.Q(email__message_id__icontains=value)
        ).distinct()
