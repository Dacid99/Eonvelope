# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the extended custom :class:`Pagination` class."""

from __future__ import annotations

from rest_framework.pagination import PageNumberPagination

from eonvelope.utils.workarounds import get_config


class Pagination(PageNumberPagination):
    """Extended pagination for the API."""

    page_size = get_config("API_DEFAULT_PAGE_SIZE")
    """The number of results per page.
    Set from :attr:`constance.get_config('API_DEFAULT_PAGE_SIZE')`.

    Note:
        Has to be set here and not in the apisettings to be apply changes directly.
    """

    page_size_query_param = "page_size"
    """The query parameter for the page size."""

    max_page_size = get_config("API_MAX_PAGE_SIZE")
    """The maximal number of results per page.
    Set from :attr:`constance.get_config('API_MAX_PAGE_SIZE')`.
    """
