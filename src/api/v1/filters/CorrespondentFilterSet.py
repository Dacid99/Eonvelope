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

"""Module with the :class:`CorrespondentFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.db.models import Q
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models import Correspondent

if TYPE_CHECKING:
    from django.db.models import Model, QuerySet


class CorrespondentFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.Correspondent`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )

    mention__iexact = filters.CharFilter(
        field_name="correspondentemails__mention", lookup_expr="iexact"
    )

    account_mail_address__icontains = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="icontains"
    )
    account_mail_address__contains = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="contains"
    )
    account_mail_address = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="exact"
    )
    account_mail_address__iexact = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="iexact"
    )
    account_mail_address__startswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="startswith"
    )
    account_mail_address__istartswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="istartswith"
    )
    account_mail_address__endswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="endswith"
    )
    account_mail_address__iendswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="iendswith"
    )
    account_mail_address__regex = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="regex"
    )
    account_mail_address__iregex = filters.CharFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="iregex"
    )
    account_mail_address__in = filters.BaseInFilter(
        field_name="emails__mailbox__account__mail_address", lookup_expr="in"
    )

    account_mail_host__icontains = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="icontains"
    )
    account_mail_host__contains = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="contains"
    )
    account_mail_host = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="exact"
    )
    account_mail_host__iexact = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="iexact"
    )
    account_mail_host__startswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="startswith"
    )
    account_mail_host__istartswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="istartswith"
    )
    account_mail_host__endswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="endswith"
    )
    account_mail_host__iendswith = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="iendswith"
    )
    account_mail_host__regex = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="regex"
    )
    account_mail_host__iregex = filters.CharFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="iregex"
    )
    account_mail_host__in = filters.BaseInFilter(
        field_name="emails__mailbox__account__mail_host", lookup_expr="in"
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = Correspondent

        fields: ClassVar[dict[str, list[str]]] = {
            "email_name": FilterSetups.TEXT,
            "real_name": FilterSetups.TEXT,
            "email_address": FilterSetups.TEXT,
            "list_id": FilterSetups.TEXT,
            "list_owner": FilterSetups.TEXT,
            "list_subscribe": FilterSetups.TEXT,
            "list_unsubscribe": FilterSetups.TEXT,
            "list_unsubscribe_post": FilterSetups.TEXT,
            "list_post": FilterSetups.TEXT,
            "list_help": FilterSetups.TEXT,
            "list_archive": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
        }

    def filter_text_fields(
        self, queryset: QuerySet[Correspondent], name: str, value: str
    ) -> QuerySet[Correspondent]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(email_address__icontains=value)
            | Q(email_name__icontains=value)
            | Q(real_name__icontains=value)
            | Q(list_id__icontains=value)
            | Q(list_owner__icontains=value)
            | Q(list_subscribe__icontains=value)
            | Q(list_unsubscribe__icontains=value)
            | Q(list_unsubscribe_post__icontains=value)
            | Q(list_post__icontains=value)
            | Q(list_help__icontains=value)
            | Q(list_archive__icontains=value)
        ).distinct()
