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

"""Module with the :class:`AccountFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models import Account


if TYPE_CHECKING:
    from django.db.models import Model


class AccountFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.Account`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = Account

        fields: ClassVar[dict[str, list[str]]] = {
            "mail_address": FilterSetups.TEXT,
            "mail_host": FilterSetups.TEXT,
            "mail_host_port": FilterSetups.INT,
            "protocol": FilterSetups.CHOICE,
            "timeout": FilterSetups.FLOAT,
            "is_healthy": FilterSetups.BOOL,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
        }

    def filter_text_fields(
        self, queryset: QuerySet[Account], name: str, value: str
    ) -> QuerySet[Account]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(mail_address__icontains=value)
            | Q(mail_host__icontains=value)
            | Q(protocol__icontains=value)
        ).distinct()
