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

from typing import TYPE_CHECKING, ClassVar, Final

from django.db import models
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models import Attachment


if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


class AttachmentFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.Attachment`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = Attachment

        fields: ClassVar[dict[str, list[str]]] = {
            "file_name": FilterSetups.TEXT,
            "content_disposition": FilterSetups.TEXT,
            "content_id": FilterSetups.TEXT,
            "content_maintype": FilterSetups.TEXT,
            "content_subtype": FilterSetups.TEXT,
            "datasize": FilterSetups.INT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "email__datetime": FilterSetups.DATETIME,
        }

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
