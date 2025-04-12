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

"""Module with the :class:`AttachmentFilter` filter set class."""

from __future__ import annotations

import django_filters
from django.forms import widgets


class AttachmentFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.AttachmentModel`."""

    file_name = django_filters.CharFilter(
        field_name="file_name",
        lookup_expr="icontains",
    )
    content_type = django_filters.CharFilter(
        field_name="content_type",
        lookup_expr="icontains",
    )
    content_disposition = django_filters.AllValuesMultipleFilter(
        field_name="content_disposition",
        lookup_expr="icontains",
    )
    datasize = django_filters.NumericRangeFilter(
        field_name="datasize",
        lookup_expr="range",
    )
    is_favorite = django_filters.BooleanFilter(
        field_name="is_favorite",
        widget=widgets.NullBooleanSelect,
    )
    email__datetime__date__lt = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__lte",
        widget=widgets.SelectDateWidget,
    )
    email__datetime__date__gt = django_filters.DateTimeFilter(
        field_name="email__datetime",
        lookup_expr="date__gt",
        widget=widgets.SelectDateWidget,
    )

    o = django_filters.OrderingFilter(
        fields=[
            "file_name",
            "content_type",
            "content_disposition",
            "datasize",
            "email__datetime",
            "created",
            "updated",
        ]
    )
