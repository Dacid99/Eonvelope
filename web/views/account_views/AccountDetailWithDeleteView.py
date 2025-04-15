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

"""Module with the :class:`AccountDetailWithDeleteView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin

from core.models.AccountModel import AccountModel
from core.utils.fetchers.exceptions import MailAccountError
from web.mixins.CustomActionMixin import CustomActionMixin
from web.mixins.TestActionMixin import TestActionMixin
from web.views.account_views.AccountFilterView import AccountFilterView


class AccountDetailWithDeleteView(
    LoginRequiredMixin, DetailView, DeletionMixin, CustomActionMixin, TestActionMixin
):
    """View for a single :class:`core.models.AccountModel.AccountModel` instance."""

    URL_NAME = AccountModel.get_detail_web_url_name()
    model = AccountModel
    template_name = "account/account_detail.html"
    context_object_name = "account"
    success_url = reverse_lazy("web:" + AccountFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return super().get_queryset().filter(user=self.request.user)

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_update_mailboxes(self, request: HttpRequest) -> HttpResponse:
        self.object = self.get_object()
        self.perform_update_mailboxes()
        self.object.refresh_from_db()
        context = self.get_context_data(object=self.object)
        return render(request, self.template_name, context)

    def perform_update_mailboxes(self) -> None:
        try:
            self.object.update_mailboxes()
        except MailAccountError:
            pass
