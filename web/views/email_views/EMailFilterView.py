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

"""Module with the :class:`EMailFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django_filters.views import FilterView

from api.v1.filters.EMailFilter import EMailFilter
from core.models.EMailModel import EMailModel


class EMailFilterView(LoginRequiredMixin, FilterView):
    """View for filtering listed :class:`core.models.EMailModel.EMailModel` instances."""

    model = EMailModel
    template_name = "email/email_filter_list.html"
    context_object_name = "emails"
    URL_NAME = "email-list"
    filterset_class = EMailFilter

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return EMailModel.objects.filter(mailbox__account__user=self.request.user)
