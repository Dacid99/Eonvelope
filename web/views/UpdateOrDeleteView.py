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

"""Module with the :class:`UpdateOrDeleteView` baseview."""

from typing import Any, override

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.views.generic.edit import DeletionMixin, UpdateView


class UpdateOrDeleteView(UpdateView, DeletionMixin):
    """A view that implements both updating and deleting."""

    delete_success_url = None
    """The URL to redirect to after deletion. Must be set."""

    success_url = None
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
