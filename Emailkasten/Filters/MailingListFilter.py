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

    _class = locals()
    for filterType in FilterSetups.TEXT:
        if filterType == "in":
            setattr(_class["MailingListFilter"],
                "correspondent_name__"+filterType,
                django_filters.BaseInFilter(field_name="correspondent__email_name", lookup_expr=filterType)
            )

            setattr(_class["MailingListFilter"],
                "correspondent_address__"+filterType,
                django_filters.BaseInFilter(field_name="correspondent__email_address", lookup_expr=filterType)
            )
        else:
            setattr(_class["MailingListFilter"],
                "correspondent_name__"+filterType,
                django_filters.CharFilter(field_name="correspondent__email_name", lookup_expr=filterType)
            )

            setattr(_class["MailingListFilter"],
                "correspondent_address__"+filterType,
                django_filters.CharFilter(field_name="correspondent__email_address", lookup_expr=filterType)
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
            "created": FilterSetups.FLOAT,
            "updated": FilterSetups.FLOAT,
        }
