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

"""Module with the :class:`MailboxDetailWithDeleteView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin

from core.constants import EmailFetchingCriterionChoices
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import FetcherError
from web.mixins.CustomActionMixin import CustomActionMixin
from web.mixins.TestActionMixin import TestActionMixin
from web.views.mailbox_views.MailboxFilterView import MailboxFilterView


class MailboxDetailWithDeleteView(
    LoginRequiredMixin, DetailView, DeletionMixin, CustomActionMixin, TestActionMixin
):
    """View for a single :class:`core.models.MailboxModel.MailboxModel` instance."""

    URL_NAME = MailboxModel.get_detail_web_url_name()
    model = MailboxModel
    template_name = "mailbox/mailbox_detail.html"
    context_object_name = "mailbox"
    success_url = reverse_lazy("web:" + MailboxFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return MailboxModel.objects.filter(account__user=self.request.user)

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_fetch_all(self, request: HttpRequest) -> HttpResponse:
        self.object = self.get_object()
        self.perform_fetch_all()
        self.object.refresh_from_db()
        context = self.get_context_data(object=self.object)
        return render(request, self.template_name, context)

    def perform_fetch_all(self) -> None:
        try:
            self.object.fetch(EmailFetchingCriterionChoices.ALL)
        except FetcherError:
            pass

    def handle_add_daemon(self, request: HttpRequest) -> HttpResponseRedirect:
        self.object = self.get_object()
        new_daemon = DaemonModel.objects.create(mailbox=self.object)
        return HttpResponseRedirect(new_daemon.get_absolute_edit_url())
