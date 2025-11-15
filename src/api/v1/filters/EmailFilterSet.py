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

"""Module with the :class:`EmailFilterSet` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters

from api.constants import FilterSetups
from core.models import Email


if TYPE_CHECKING:
    from django.db.models import Model


class EmailFilterSet(filters.FilterSet):
    """The filter class for :class:`core.models.Email`."""

    search = filters.CharFilter(
        method="filter_text_fields",
    )

    correspondent_mention = filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="exact"
    )

    correspondent_mention__icontains = filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="icontains"
    )

    correspondent_mention__in = filters.BaseInFilter(
        field_name="emailcorrespondents__mention", lookup_expr="in"
    )

    headers__contains = filters.CharFilter(field_name="headers", lookup_expr="contains")

    headers__icontains = filters.CharFilter(
        field_name="headers", lookup_expr="icontains"
    )

    headers__contained_by = filters.CharFilter(
        field_name="headers", lookup_expr="contained_by"
    )

    headers__regex = filters.CharFilter(field_name="headers", lookup_expr="regex")

    headers__iregex = filters.CharFilter(field_name="headers", lookup_expr="iregex")

    headers__has_key = filters.CharFilter(field_name="headers", lookup_expr="has_key")

    headers__has_keys = filters.CharFilter(field_name="headers", lookup_expr="has_keys")

    headers__has_any_keys = filters.CharFilter(
        field_name="headers", lookup_expr="has_any_keys"
    )

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = Email

        fields: ClassVar[dict[str, list[str]]] = {
            "message_id": FilterSetups.TEXT,
            "datetime": FilterSetups.DATETIME,
            "subject": FilterSetups.TEXT,
            "plain_bodytext": FilterSetups.TEXT,
            "html_bodytext": FilterSetups.TEXT,
            "datasize": FilterSetups.INT,
            "x_spam": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "attachments__file_name": FilterSetups.TEXT,
            "correspondents__email_name": FilterSetups.TEXT,
            "correspondents__email_address": FilterSetups.TEXT,
            "mailbox__name": FilterSetups.TEXT,
            "mailbox__account__mail_address": FilterSetups.TEXT,
            "mailbox__account__mail_host": FilterSetups.TEXT,
        }

    def filter_text_fields(
        self, queryset: QuerySet[Email], name: str, value: str
    ) -> QuerySet[Email]:
        """Filters textfields in the model.

        Args:
            queryset: The basic queryset to filter.
            name: The name of the filterfield.
            value: The value to filter by.

        Returns:
            The filtered queryset.
        """
        return queryset.filter(
            Q(message_id__icontains=value)
            | Q(subject__icontains=value)
            | Q(plain_bodytext__icontains=value)
            | Q(html_bodytext__icontains=value)
            | Q(headers__has_any_keys=value)
            | Q(correspondents__email_address=value)
            | Q(attachments__file_name=value)
        ).distinct()
