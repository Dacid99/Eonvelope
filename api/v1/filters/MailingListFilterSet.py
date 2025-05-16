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

"""Module with the :class:`MailingListFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models.MailingList import MailingList


if TYPE_CHECKING:
    from django.db.models import Model


class MailingListFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.MailingList.MailingList`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = MailingList

        fields: ClassVar[dict[str, list[str]]] = {
            "list_id": FilterSetups.TEXT,
            "list_owner": FilterSetups.TEXT,
            "list_subscribe": FilterSetups.TEXT,
            "list_unsubscribe": FilterSetups.TEXT,
            "list_post": FilterSetups.TEXT,
            "list_help": FilterSetups.TEXT,
            "list_archive": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
        }

    def filter_text_fields(
        self, queryset: QuerySet[MailingList], name: str, value: str
    ) -> QuerySet[MailingList]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(list_id__icontains=value)
            | Q(list_owner__icontains=value)
            | Q(list_subscribe__icontains=value)
            | Q(list_unsubscribe__icontains=value)
            | Q(list_post__icontains=value)
            | Q(list_help__icontains=value)
            | Q(list_archive__icontains=value)
        ).distinct()
