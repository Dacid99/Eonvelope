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

from api.constants import FilterSetups
from core.models.MailingListModel import MailingListModel


class MailingListFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.MailingListModel`."""

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
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "correspondent__email_name": FilterSetups.TEXT,
            "correspondent__email_address": FilterSetups.TEXT,
        }
