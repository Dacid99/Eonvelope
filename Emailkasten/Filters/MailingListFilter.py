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

"""Module with the :class:`MailingListFilter` filter provider class."""

import django_filters

from ..constants import FilterSetups
from ..Models.MailingListModel import MailingListModel


class MailingListFilter(django_filters.FilterSet):
    """The filter class for :class:`Emailkasten.Models.MailingListModel`."""

    correspondent_name__icontains = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="icontains"
    )

    correspondent_name__contains = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="contains"
    )

    correspondent_name__exact = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="exact"
    )

    correspondent_name__iexact = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="iexact"
    )

    correspondent_name__startswith = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="startswith"
    )

    correspondent_name__istartswith = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="istartswith"
    )

    correspondent_name__endswith = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="endswith"
    )

    correspondent_name__iendswith = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="iendswith"
    )

    correspondent_name__regex = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="regex"
    )

    correspondent_name__iregex = django_filters.CharFilter(
        field_name="correspondent__email_name", lookup_expr="iregex"
    )

    correspondent_name__in = django_filters.BaseInFilter(
        field_name="correspondent__email_name", lookup_expr="in"
    )

    correspondent_address__icontains = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="icontains"
    )

    correspondent_address__contains = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="contains"
    )

    correspondent_address__exact = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="exact"
    )

    correspondent_address__iexact = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="iexact"
    )

    correspondent_address__startswith = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="startswith"
    )

    correspondent_address__istartswith = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="istartswith"
    )

    correspondent_address__endswith = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="endswith"
    )

    correspondent_address__iendswith = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="iendswith"
    )

    correspondent_address__regex = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="regex"
    )

    correspondent_address__iregex = django_filters.CharFilter(
        field_name="correspondent__email_address", lookup_expr="iregex"
    )

    correspondent_address__in = django_filters.BaseInFilter(
        field_name="correspondent__email_address", lookup_expr="in"
    )

    class Meta:
        """Metadata class for the filter."""

        model = MailingListModel
        fields = {
            "list_id": FilterSetups.TEXT,
            "list_owner": FilterSetups.TEXT,
            "list_subscribe": FilterSetups.TEXT,
            "list_unsubscribe": FilterSetups.TEXT,
            "list_post": FilterSetups.TEXT,
            "list_help": FilterSetups.TEXT,
            "list_archive": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.FLOAT,
            "updated": FilterSetups.FLOAT,
        }
