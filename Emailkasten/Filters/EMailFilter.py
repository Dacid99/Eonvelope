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

from ..constants import FilterSetups
from ..Models.EMailModel import EMailModel


class EMailFilter(django_filters.FilterSet):
    """The filter class for :class:`Emailkasten.Models.EMailModel`."""

    attachment_name__icontains = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="icontains"
    )

    attachment_name__contains = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="contains"
    )

    attachment_name__exact = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="exact"
    )

    attachment_name__iexact = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="iexact"
    )

    attachment_name__startswith = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="startswith"
    )

    attachment_name__istartswith = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="istartswith"
    )

    attachment_name__endswith = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="endswith"
    )

    attachment_name__iendswith = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="iendswith"
    )

    attachment_name__regex = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="regex"
    )

    attachment_name__iregex = django_filters.CharFilter(
        field_name="attachments__file_name", lookup_expr="iregex"
    )

    attachment_name__in = django_filters.BaseInFilter(
        field_name="attachments__file_name", lookup_expr="in"
    )

    correspondent_name__icontains = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="icontains"
    )

    correspondent_name__contains = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="contains"
    )

    correspondent_name__exact = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="exact"
    )

    correspondent_name__iexact = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="iexact"
    )

    correspondent_name__startswith = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="startswith"
    )

    correspondent_name__istartswith = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="istartswith"
    )

    correspondent_name__endswith = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="endswith"
    )

    correspondent_name__iendswith = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="iendswith"
    )

    correspondent_name__regex = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="regex"
    )

    correspondent_name__iregex = django_filters.CharFilter(
        field_name="correspondents__email_name", lookup_expr="iregex"
    )

    correspondent_name__in = django_filters.BaseInFilter(
        field_name="correspondents__email_name", lookup_expr="in"
    )

    correspondent_address__icontains = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="icontains"
    )

    correspondent_address__contains = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="contains"
    )

    correspondent_address__exact = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="exact"
    )

    correspondent_address__iexact = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="iexact"
    )

    correspondent_address__startswith = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="startswith"
    )

    correspondent_address__istartswith = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="istartswith"
    )

    correspondent_address__endswith = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="endswith"
    )

    correspondent_address__iendswith = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="iendswith"
    )

    correspondent_address__regex = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="regex"
    )

    correspondent_address__iregex = django_filters.CharFilter(
        field_name="correspondents__email_address", lookup_expr="iregex"
    )

    correspondent_address__in = django_filters.BaseInFilter(
        field_name="correspondents__email_address", lookup_expr="in"
    )

    correspondent_mention__exact = django_filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="exact"
    )

    correspondent_mention__icontains = django_filters.CharFilter(
        field_name="emailcorrespondents__mention", lookup_expr="icontains"
    )

    correspondent_mention__in = django_filters.BaseInFilter(
        field_name="emailcorrespondents__mention", lookup_expr="in"
    )

    mailinglist_list_id__icontains = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="icontains"
    )

    mailinglist_list_id__contains = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="contains"
    )

    mailinglist_list_id__exact = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="exact"
    )

    mailinglist_list_id__iexact = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="iexact"
    )

    mailinglist_list_id__startswith = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="startswith"
    )

    mailinglist_list_id__istartswith = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="istartswith"
    )

    mailinglist_list_id__endswith = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="endswith"
    )

    mailinglist_list_id__iendswith = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="iendswith"
    )

    mailinglist_list_id__regex = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="regex"
    )

    mailinglist_list_id__iregex = django_filters.CharFilter(
        field_name="mailinglist__list_id", lookup_expr="iregex"
    )

    mailinglist_list_id__in = django_filters.BaseInFilter(
        field_name="mailinglist__list_id", lookup_expr="in"
    )

    mailinglist_list_owner__icontains = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="icontains"
    )

    mailinglist_list_owner__contains = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="contains"
    )

    mailinglist_list_owner__exact = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="exact"
    )

    mailinglist_list_owner__iexact = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="iexact"
    )

    mailinglist_list_owner__startswith = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="startswith"
    )

    mailinglist_list_owner__istartswith = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="istartswith"
    )

    mailinglist_list_owner__endswith = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="endswith"
    )

    mailinglist_list_owner__iendswith = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="iendswith"
    )

    mailinglist_list_owner__regex = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="regex"
    )

    mailinglist_list_owner__iregex = django_filters.CharFilter(
        field_name="mailinglist__list_owner", lookup_expr="iregex"
    )

    mailinglist_list_owner__in = django_filters.BaseInFilter(
        field_name="mailinglist__list_owner", lookup_expr="in"
    )

    account_address__icontains = django_filters.CharFilter(
        field_name="account__address", lookup_expr="icontains"
    )

    account_address__contains = django_filters.CharFilter(
        field_name="account__address", lookup_expr="contains"
    )

    account_address__exact = django_filters.CharFilter(
        field_name="account__address", lookup_expr="exact"
    )

    account_address__iexact = django_filters.CharFilter(
        field_name="account__address", lookup_expr="iexact"
    )

    account_address__startswith = django_filters.CharFilter(
        field_name="account__address", lookup_expr="startswith"
    )

    account_address__istartswith = django_filters.CharFilter(
        field_name="account__address", lookup_expr="istartswith"
    )

    account_address__endswith = django_filters.CharFilter(
        field_name="account__address", lookup_expr="endswith"
    )

    account_address__iendswith = django_filters.CharFilter(
        field_name="account__address", lookup_expr="iendswith"
    )

    account_address__regex = django_filters.CharFilter(
        field_name="account__address", lookup_expr="regex"
    )

    account_address__iregex = django_filters.CharFilter(
        field_name="account__address", lookup_expr="iregex"
    )

    account_address__in = django_filters.BaseInFilter(
        field_name="account__address", lookup_expr="in"
    )

    account_host__icontains = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="icontains"
    )

    account_host__contains = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="contains"
    )

    account_host__exact = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="exact"
    )

    account_host__iexact = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="iexact"
    )

    account_host__startswith = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="startswith"
    )

    account_host__istartswith = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="istartswith"
    )

    account_host__endswith = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="endswith"
    )

    account_host__iendswith = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="iendswith"
    )

    account_host__regex = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="regex"
    )

    account_host__iregex = django_filters.CharFilter(
        field_name="account__mail_host", lookup_expr="iregex"
    )

    account_host__in = django_filters.BaseInFilter(
        field_name="account__mail_host", lookup_expr="in"
    )

    class Meta:
        """Metadata class for the filter."""

        model = EMailModel
        fields = {
            "message_id": FilterSetups.TEXT,
            "datetime": FilterSetups.FLOAT,
            "email_subject": FilterSetups.TEXT,
            "bodytext": FilterSetups.TEXT,
            "datasize": FilterSetups.INT,
            "comments": FilterSetups.TEXT,
            "keywords": FilterSetups.TEXT,
            "importance": FilterSetups.TEXT,
            "priority": FilterSetups.TEXT,
            "precedence": FilterSetups.TEXT,
            "user_agent": FilterSetups.TEXT,
            "auto_submitted": FilterSetups.TEXT,
            "content_type": FilterSetups.TEXT,
            "content_language": FilterSetups.TEXT,
            "content_location": FilterSetups.TEXT,
            "x_priority": FilterSetups.TEXT,
            "x_originated_client": FilterSetups.TEXT,
            "x_spam": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.FLOAT,
            "updated": FilterSetups.FLOAT,
        }
