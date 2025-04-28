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

"""Module with the :class:`AccountUpdateView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy

from core.models.AccountModel import AccountModel
from web.views.UpdateOrDeleteView import UpdateOrDeleteView

from ...forms.account_forms.BaseAccountForm import BaseAccountForm
from .AccountFilterView import AccountFilterView


class AccountUpdateOrDeleteView(LoginRequiredMixin, UpdateOrDeleteView):
    """View for updating or deleting a single :class:`core.models.AccountModel.AccountModel` instance."""

    model = AccountModel
    form_class = BaseAccountForm
    template_name = "web/account/account_edit.html"
    context_object_name = "account"
    delete_success_url = reverse_lazy("web:" + AccountFilterView.URL_NAME)
    URL_NAME = AccountModel.get_edit_web_url_name()

    @override
    def get_queryset(self) -> QuerySet[AccountModel]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        return super().get_queryset().filter(user=self.request.user)
