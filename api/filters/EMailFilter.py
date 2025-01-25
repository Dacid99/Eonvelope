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

from Emailkasten.constants import FilterSetups
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

    class Meta:
        """Metadata class for the filter."""

        model = EMailModel
        fields = {
            "message_id": FilterSetups.TEXT,
            "datetime": FilterSetups.DATETIME,
            "email_subject": FilterSetups.TEXT,
            "bodytext": FilterSetups.TEXT,
            "datasize": FilterSetups.INT,
            "comments": FilterSetups.TEXT,
            "keywords": FilterSetups.TEXT,
            "importance": FilterSetups.TEXT,
            "priority": FilterSetups.TEXT,
            "precedence": FilterSetups.TEXT,
            "received": FilterSetups.TEXT,
            "user_agent": FilterSetups.TEXT,
            "auto_submitted": FilterSetups.TEXT,
            "content_type": FilterSetups.TEXT,
            "content_language": FilterSetups.TEXT,
            "content_location": FilterSetups.TEXT,
            "x_priority": FilterSetups.TEXT,
            "x_originated_client": FilterSetups.TEXT,
            "x_spam": FilterSetups.TEXT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "attachments__file_name": FilterSetups.TEXT,
            "correspondents__email_name": FilterSetups.TEXT,
            "correspondents__email_address": FilterSetups.TEXT,
            "account__mail_address": FilterSetups.TEXT,
            "account__mail_host": FilterSetups.TEXT,
            "mailinglist__list_id": FilterSetups.TEXT,
            "mailinglist__list_owner": FilterSetups.TEXT
        }
