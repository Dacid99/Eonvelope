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
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin
from rest_framework import status

from core.models.MailboxModel import MailboxModel
from web.mixins.TestActionMixin import TestActionMixin
from web.views.mailbox_views.MailboxFilterView import MailboxFilterView


class MailboxDetailWithDeleteView(
    LoginRequiredMixin, DetailView, DeletionMixin, TestActionMixin
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
        if "test" in request.POST:
            return TestActionMixin.post(self, request)
        return HttpResponse(status=status.HTTP_204_NO_CONTENT)
