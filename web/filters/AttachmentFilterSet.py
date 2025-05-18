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

"""Module with the :class:`AttachmentFilterSet` filter set class."""

from __future__ import annotations

import django_filters
from django.forms import widgets

from ..utils.widgets import AdaptedSelectDateWidget


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

    file_name__icontains = django_filters.CharFilter(
        field_name="file_name",
        lookup_expr="icontains",
    )
    content_maintype = django_filters.AllValuesMultipleFilter(
        field_name="content_maintype",
    )
    content_subtype = django_filters.AllValuesMultipleFilter(
        field_name="content_subtype",
    )
    content_id__icontains = django_filters.CharFilter(
        field_name="content_id",
        lookup_expr="icontains",
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
        label="Received before",
        widget=AdaptedSelectDateWidget,
    )
    email__datetime__date__gte = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__gte",
        label="Received after",
        widget=AdaptedSelectDateWidget,
    )
