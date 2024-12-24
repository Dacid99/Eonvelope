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

import django_filters

from ..constants import FilterSetups
from ..Models.CorrespondentModel import CorrespondentModel


class CorrespondentFilter(django_filters.FilterSet):
    """The filter class for :class:`Emailkasten.Models.CorrespondentModel`."""

    mention__iexact = django_filters.CharFilter(
        field_name="correspondentemails__mention", lookup_expr="iexact"
    )

    account_mail_address__icontains = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="icontains"
    )

    account_mail_address__contains = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="contains"
    )

    account_mail_address__exact = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="exact"
    )

    account_mail_address__iexact = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="iexact"
    )

    account_mail_address__startswith = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="startswith"
    )

    account_mail_address__istartswith = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="istartswith"
    )

    account_mail_address__endswith = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="endswith"
    )

    account_mail_address__iendswith = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="iendswith"
    )

    account_mail_address__regex = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="regex"
    )

    account_mail_address__iregex = django_filters.CharFilter(
        field_name="emails__account__mail_address", lookup_expr="iregex"
    )

    account_mail_address__in = django_filters.BaseInFilter(
        field_name="emails__account__mail_address", lookup_expr="in"
    )

    account_mail_host__icontains = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="icontains"
    )

    account_mail_host__contains = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="contains"
    )

    account_mail_host__exact = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="exact"
    )

    account_mail_host__iexact = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="iexact"
    )

    account_mail_host__startswith = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="startswith"
    )

    account_mail_host__istartswith = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="istartswith"
    )

    account_mail_host__endswith = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="endswith"
    )

    account_mail_host__iendswith = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="iendswith"
    )

    account_mail_host__regex = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="regex"
    )

    account_mail_host__iregex = django_filters.CharFilter(
        field_name="emails__account__mail_host", lookup_expr="iregex"
    )

    account_mail_host__in = django_filters.BaseInFilter(
        field_name="emails__account__mail_host", lookup_expr="in"
    )

    class Meta:
        model = CorrespondentModel
        fields = {
            "email_name": FilterSetups.TEXT,
            "email_address": FilterSetups.TEXT,
            "created": FilterSetups.FLOAT,
            "updated": FilterSetups.FLOAT,
        }
