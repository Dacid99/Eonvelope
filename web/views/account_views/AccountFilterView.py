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

"""Module with the :class:`AccountFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet

from core.models.AccountModel import AccountModel

from ...filters.AccountFilter import AccountFilter
from ..FilterPageView import FilterPageView


class AccountFilterView(LoginRequiredMixin, FilterPageView):
    """View for filtering listed :class:`core.models.AccountModel.AccountModel` instances."""

    URL_NAME = AccountModel.get_list_web_url_name()
    model = AccountModel
    template_name = "web/account/account_filter_list.html"
    filterset_class = AccountFilter
    paginate_by = 25

    @override
    def get_queryset(self) -> QuerySet[AccountModel]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        return super().get_queryset().filter(user=self.request.user)
