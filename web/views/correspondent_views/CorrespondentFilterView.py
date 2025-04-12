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

"""Module with the :class:`CorrespondentFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django_filters.views import FilterView

from core.models.CorrespondentModel import CorrespondentModel

from ...filters.CorrespondentFilter import CorrespondentFilter


class CorrespondentFilterView(LoginRequiredMixin, FilterView):
    """View for filtering listed :class:`core.models.CorrespondentModel.CorrespondentModel` instances."""

    model = CorrespondentModel
    template_name = "correspondent/correspondent_filter_list.html"
    context_object_name = "correspondents"
    URL_NAME = CorrespondentModel.get_list_web_url_name()
    filterset_class = CorrespondentFilter

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return CorrespondentModel.objects.filter(
            emails__mailbox__account__user=self.request.user
        ).distinct()
