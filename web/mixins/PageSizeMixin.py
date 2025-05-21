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

"""Module with the :class:`web.views.FilterPageView.FilterPageView`."""

from typing import Any

from django.db.models import QuerySet

from Emailkasten.utils.workarounds import get_config


class PageSizeMixin:
    """An extended :class:`django_filters.views.FilterView` with fixed pagination."""

    page_size_kwarg = "page_size"
    paginate_by = get_config("WEB_DEFAULT_PAGE_SIZE")

    def get_paginate_by(self, queryset: QuerySet) -> int:
        """Extended method to allow variable page sizes.

        Returns:
            The requested page size or the `paginate_by` value.
        """
        return (
            self.kwargs.get(self.page_size_kwarg)
            or self.request.GET.get(self.page_size_kwarg)
            or super().get_paginate_by(queryset)
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended method to allow variable page sizes.

        Returns:
            The context with a page_size added to it.
        """
        return super().get_context_data(
            page_size=self.get_paginate_by(self.object_list), **kwargs
        )
