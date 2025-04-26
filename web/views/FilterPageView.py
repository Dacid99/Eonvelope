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

"""Module with the :func:`web.views.FilterpageView.FilterpageView`."""

from typing import Any, override

from django_filters.views import FilterView


class FilterPageView(FilterView):
    """An extended :class:`django_filters.views.FilterView` with fixed pagination."""

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended method to pass the query parameters to the context.

        Note:
            Follows the fix proposed in https://jeffpohlmeyer.com/django-filters-with-pagination .

        Returns:
            The view's context with added query parameters.
        """
        context = super().get_context_data(**kwargs)
        context["query"] = {}
        for query_param, query_value in context["filter"].data.items():
            if query_param != "page":
                context["query"][query_param] = query_value

        return context
