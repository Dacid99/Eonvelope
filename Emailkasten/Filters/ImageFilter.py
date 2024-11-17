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

from ..Models.ImageModel import ImageModel


class ImageFilter(django_filters.FilterSet):
    """The filter class for :class:`Emailkasten.Models.ImageModel`."""

    datetime__lte = django_filters.DateTimeFilter(
        field_name="email__datetime", lookup_expr="lte"
    )

    datetime__gte = django_filters.DateTimeFilter(
        field_name="email__datetime", lookup_expr="gte"
    )

    class Meta:
        model = ImageModel
        fields = {
            "file_name": [
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
            "datasize": [
                "lte",
                "gte",
                "lt",
                "gt",
                "exact",
                "in"
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
