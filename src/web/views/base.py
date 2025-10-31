# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with baseviews for the Emailkasten webapp."""

from typing import Any, override

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin, UpdateView
from django_filters.views import FilterView

from web.mixins import PageSizeMixin


class FilterPageView(PageSizeMixin, FilterView):
    """An extended :class:`django_filters.views.FilterView` with fixed pagination."""

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended method to pass the query parameters to the context.

        References:
            https://jeffpohlmeyer.com/django-filters-with-pagination

        Returns:
            The view's context with added query parameters.
        """
        context = super().get_context_data(**kwargs)
        context["query"] = {}
        for query_param, query_value in context["filter"].data.items():
            if not query_param.startswith("page"):
                context["query"][query_param] = query_value

        return context


class DetailWithDeleteView(DetailView, DeletionMixin):
    """A view for model details with an option to delete."""


class UpdateOrDeleteView(UpdateView, DeletionMixin):
    """A view that implements both updating and deleting."""

    delete_success_url: str | None = None
    """The URL to redirect to after deletion. Must be set."""

    success_url: str | None = None
    """The URL to redirect to after form submission.
    If this is not set, the models get_absolute_url method is used.
    """

    @override
    def get_success_url(self) -> str:
        """Overridden method to redirect to filter-list after `delete` else to detail."""
        if "delete" in self.request.POST:
            if self.delete_success_url:
                return self.delete_success_url
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a delete_success_url."
            )
        return UpdateView.get_success_url(self)

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Overridden method to distinguish the `delete` button."""
        if "delete" in request.POST:
            return DeletionMixin.post(self, request, *args, **kwargs)
        return UpdateView.post(self, request, *args, **kwargs)
