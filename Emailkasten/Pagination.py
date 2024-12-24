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

from rest_framework.pagination import PageNumberPagination

from .constants import APIConfiguration


class Pagination(PageNumberPagination):
    """Extended pagination for the API."""

    page_size = APIConfiguration.DEFAULT_PAGE_SIZE
    """The number of results per page.
        Set from :attr:`Emailkasten.constants.APIConfiguration.DEFAULT_PAGE_SIZE`."""

    page_size_query_param = 'page_size'
    """The query parameter for the page size."""

    page_query_param = 'page'
    """The query parameter for the page number."""


    def get_page_size(self, request):
        """Extends :func:`rest_framework.pagination.PageNumberPagination.get_page_size`.
            to add an 'all' option to the query.

        Note:
            May be unnecessary.
        """
        if request.query_params.get('all') == 'true':
            return None
        return super().get_page_size(request)


    def paginate_queryset(self, queryset, request, view=None):
        """Extends :func:`rest_framework.pagination.PageNumberPagination.paginate_queryset`.
            to add an 'all' option to the query.
        """
        if request.query_params.get('all') == 'true':
            return list(queryset)
        return super().paginate_queryset(queryset, request, view)
