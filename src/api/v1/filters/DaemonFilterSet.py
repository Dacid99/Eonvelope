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

"""Module with the :class:`DaemonFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.db.models import Q
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models import Daemon

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


class DaemonFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.Mailbox`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )
    mail_address__icontains = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="icontains"
    )
    mail_address__contains = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="contains"
    )
    mail_address = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="exact"
    )
    mail_address__iexact = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iexact"
    )
    mail_address__startswith = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="startswith"
    )
    mail_address__istartswith = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="istartswith"
    )
    mail_address__endswith = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="endswith"
    )
    mail_address__iendswith = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iendswith"
    )
    mail_address__regex = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="regex"
    )
    mail_address__iregex = filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iregex"
    )
    mail_address__in = filters.BaseInFilter(
        field_name="mailbox__account__mail_address", lookup_expr="in"
    )

    mail_host__icontains = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="icontains"
    )
    mail_host__contains = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="contains"
    )
    mail_host = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="exact"
    )
    mail_host__iexact = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iexact"
    )
    mail_host__startswith = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="startswith"
    )
    mail_host__istartswith = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="istartswith"
    )
    mail_host__endswith = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="endswith"
    )
    mail_host__iendswith = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iendswith"
    )
    mail_host__regex = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="regex"
    )
    mail_host__iregex = filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iregex"
    )
    mail_host__in = filters.BaseInFilter(
        field_name="mailbox__account__mail_host", lookup_expr="in"
    )

    protocol__iexact = filters.CharFilter(
        field_name="mailbox__account__protocol", lookup_expr="iexact"
    )
    protocol__icontains = filters.CharFilter(
        field_name="mailbox__account__protocol", lookup_expr="icontains"
    )
    protocol__in = filters.BaseInFilter(
        field_name="mailbox__account__protocol", lookup_expr="in"
    )

    account__is_healthy = filters.BooleanFilter(
        field_name="mailbox__account__is_healthy", lookup_expr="exact"
    )

    enabled = filters.BooleanFilter(
        field_name="celery_task__enabled", lookup_expr="exact"
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = Daemon

        fields: ClassVar[dict[str, list[str]]] = {
            "uuid": ["exact", "contains"],
            "fetching_criterion": FilterSetups.CHOICE,
            "fetching_criterion_arg": FilterSetups.TEXT,
            "interval__every": FilterSetups.INT,
            "interval__period": FilterSetups.TEXT,
            "celery_task__last_run_at": FilterSetups.DATETIME,
            "celery_task__total_run_count": FilterSetups.INT,
            "is_healthy": FilterSetups.BOOL,
            "last_error": FilterSetups.TEXT,
            "last_error_occurred_at": FilterSetups.DATETIME,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "mailbox__name": FilterSetups.TEXT,
            "mailbox__is_healthy": FilterSetups.BOOL,
        }

    def filter_text_fields(
        self, queryset: QuerySet[Daemon], name: str, value: str
    ) -> QuerySet[Daemon]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(uuid__icontains=value)
            | Q(fetching_criterion__icontains=value)
            | Q(fetching_criterion_arg__icontains=value)
            | Q(mailbox__name__icontains=value)
            | Q(mailbox__account__mail_address__icontains=value)
            | Q(mailbox__account__mail_host__icontains=value)
            | Q(mailbox__account__protocol__icontains=value)
        )
