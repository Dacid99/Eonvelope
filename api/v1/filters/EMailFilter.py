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

"""Module with the :class:`EMailFilter` filter provider class."""

import django_filters

from api.constants import FilterSetups
from core.models.EMailModel import EMailModel


class EMailFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.EMailModel`."""

    correspondent_mention = django_filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="exact"
    )

    correspondent_mention__icontains = django_filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="icontains"
    )

    correspondent_mention__in = django_filters.BaseInFilter(
        field_name="emailcorrespondents__mention", lookup_expr="in"
    )

    headers__contains = django_filters.CharFilter(
        field_name="headers", lookup_expr="contains"
    )

    headers__icontains = django_filters.CharFilter(
        field_name="headers", lookup_expr="icontains"
    )

    headers__contained_by = django_filters.CharFilter(
        field_name="headers", lookup_expr="contained_by"
    )

    headers__regex = django_filters.CharFilter(
        field_name="headers", lookup_expr="regex"
    )

    headers__iregex = django_filters.CharFilter(
        field_name="headers", lookup_expr="iregex"
    )

    headers__has_key = django_filters.CharFilter(
        field_name="headers", lookup_expr="has_key"
    )

    headers__has_keys = django_filters.CharFilter(
        field_name="headers", lookup_expr="has_keys"
    )

    headers__has_any_keys = django_filters.CharFilter(
        field_name="headers", lookup_expr="has_any_keys"
    )

    class Meta:
        """Metadata class for the filter."""

        model = EMailModel
        fields = {
            "message_id": FilterSetups.TEXT,
            "datetime": FilterSetups.DATETIME,
            "email_subject": FilterSetups.TEXT,
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
            "mailinglist__list_id": FilterSetups.TEXT,
            "mailinglist__list_owner": FilterSetups.TEXT,
        }
