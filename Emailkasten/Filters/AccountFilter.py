# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import django_filters

from ..Models.AccountModel import AccountModel


class AccountFilter(django_filters.FilterSet):
    """The filter class for :class:`Emailkasten.Models.AccountModel`."""

    class Meta:
        model = AccountModel
        fields = {
            "mail_address": [
                "icontains",
                "contains",
                "exact",
                "iexact",
                "startswith",
                "istartswith",
                "endswith",
                "iendswith",
                "regex",
                "iregex",
                "in",
            ],
            "mail_host": [
                "icontains",
                "contains",
                "exact",
                "iexact",
                "startswith",
                "istartswith",
                "endswith",
                "iendswith",
                "regex",
                "iregex",
                "in",
            ],
            "mail_host_port": [
                "exact",
                "lte",
                "gte",
                "lt",
                "gt",
                "in"
            ],
            "protocol": [
                "icontains",
                "iexact",
                "in"
            ],
            "timeout": [
                "lte",
                "gte"
            ],
            "is_healthy": [
                "exact"
            ],
            "created": [
                "lte",
                "gte"
            ],
            "updated": [
                "lte",
                "gte"
            ],
        }
