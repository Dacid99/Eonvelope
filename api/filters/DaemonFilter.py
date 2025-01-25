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

"""Module with the :class:`DaemonFilter` filter provider class."""

import django_filters

from Emailkasten.constants import FilterSetups
from core.models.DaemonModel import DaemonModel

class DaemonFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.MailboxModel`."""

    mail_address__icontains = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="icontains"
    )
    mail_address__contains = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="contains"
    )
    mail_address = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="exact"
    )
    mail_address__iexact = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iexact"
    )
    mail_address__startswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="startswith"
    )
    mail_address__istartswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="istartswith"
    )
    mail_address__endswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="endswith"
    )
    mail_address__iendswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iendswith"
    )
    mail_address__regex = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="regex"
    )
    mail_address__iregex = django_filters.CharFilter(
        field_name="mailbox__account__mail_address", lookup_expr="iregex"
    )
    mail_address__in = django_filters.BaseInFilter(
        field_name="mailbox__account__mail_address", lookup_expr="in"
    )

    mail_host__icontains = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="icontains"
    )
    mail_host__contains = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="contains"
    )
    mail_host = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="exact"
    )
    mail_host__iexact = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iexact"
    )
    mail_host__startswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="startswith"
    )
    mail_host__istartswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="istartswith"
    )
    mail_host__endswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="endswith"
    )
    mail_host__iendswith = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iendswith"
    )
    mail_host__regex = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="regex"
    )
    mail_host__iregex = django_filters.CharFilter(
        field_name="mailbox__account__mail_host", lookup_expr="iregex"
    )
    mail_host__in = django_filters.BaseInFilter(
        field_name="mailbox__account__mail_host", lookup_expr="in"
    )

    protocol__iexact = django_filters.CharFilter(
        field_name="mailbox__account__protocol", lookup_expr="iexact"
    )
    protocol__icontains = django_filters.CharFilter(
        field_name="mailbox__account__protocol", lookup_expr="icontains"
    )
    protocol__in = django_filters.BaseInFilter(
        field_name="mailbox__account__protocol", lookup_expr="in"
    )

    account__is_healthy = django_filters.BooleanFilter(
        field_name="mailbox__account__is_healthy", lookup_expr="exact"
    )

    class Meta:
        """Metadata class for the filter."""

        model = DaemonModel
        fields = {
            "uuid": ["exact", "contains"],
            "fetching_criterion": FilterSetups.CHOICE,
            "cycle_interval": FilterSetups.INT,
            "restart_time": FilterSetups.INT,
            "is_running": FilterSetups.BOOL,
            "is_healthy": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "mailbox__name": FilterSetups.TEXT,
            "mailbox__is_healthy": FilterSetups.BOOL
        }
