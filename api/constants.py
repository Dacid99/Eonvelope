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

"""Module with the constant values for the :mod:`api` app."""

import os
from typing import Final


class APIv1Configuration:
    """Namespace class for all configuration constants of the API."""

    DEFAULT_PAGE_SIZE: Final[int] = 20
    """The default number of entries per paginated response."""

    MAX_PAGE_SIZE: Final[int] = 200
    """The maximal number of entries per paginated response."""

    REGISTRATION_ENABLED: Final[bool] = os.environ.get("REGISTRATION_ENABLED", False)
    """Whether reegistration of new users is enabled."""



class FilterSetups:
    """Namespace class for all filter setups for different field types."""

    TEXT: Final[list[str]] = [
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
        "in"
    ]
    """Standard filter options for text fields."""

    DATETIME: Final[list[str]] = [
        "date",
        "date__gte",
        "date__lte",
        "date__gt",
        "date__lt",
        "date__in",
        "date__range",
        "time",
        "time__gte",
        "time__lte",
        "time__gt",
        "time__lt",
        "time__in",
        "time__range",
        "iso_year",
        "iso_year",
        "iso_year__gte",
        "iso_year__lte",
        "iso_year__gt",
        "iso_year__lt",
        "iso_year__in",
        "iso_year__range",
        "month",
        "month__gte",
        "month__lte",
        "month__gt",
        "month__lt",
        "month__in",
        "month__range",
        "quarter",
        "quarter__gte",
        "quarter__lte",
        "quarter__gt",
        "quarter__lt",
        "quarter__in",
        "quarter__range",
        "week",
        "week__gte",
        "week__lte",
        "week__gt",
        "week__lt",
        "week__in",
        "week__range",
        "iso_week_day",
        "iso_week_day__gte",
        "iso_week_day__lte",
        "iso_week_day__gt",
        "iso_week_day__lt",
        "iso_week_day__in",
        "iso_week_day__range",
        "day",
        "day__gte",
        "day__lte",
        "day__gt",
        "day__lt",
        "day__in",
        "day__range",
        "hour",
        "hour__gte",
        "hour__lte",
        "hour__gt",
        "hour__lt",
        "hour__in",
        "hour__range",
        "minute",
        "minute__gte",
        "minute__lte",
        "minute__gt",
        "minute__lt",
        "minute__in",
        "minute__range",
        "second",
        "second__gte",
        "second__lte",
        "second__gt",
        "second__lt",
        "second__in",
        "second__range",
    ]

    FLOAT: Final[list[str]] = [
        "lte",
        "gte",
        "range"
    ]
    """Standard filter options for float fields."""


    INT: Final[list[str]] = [
        "lte",
        "gte",
        "lt",
        "gt",
        "exact",
        "in",
        "range"
    ]
    """Standard filter options for integer fields."""


    BOOL: Final[list[str]] = ["exact"]
    """Standard filter options for boolean fields."""


    CHOICE: Final[list[str]] = [
        "icontains",
        "iexact",
        "in"
    ]
    """Standard filter options for fields with constant choices."""
