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

"""Module with the :class:`web.views.AccountDetailWithDeleteView` view."""

from typing import Any, override

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import DeletionMixin

from core.models import Account, Email
from core.utils.fetchers.exceptions import MailAccountError
from web.mixins.CustomActionMixin import CustomActionMixin
from web.mixins.TestActionMixin import TestActionMixin

from ..DetailWithDeleteView import DetailWithDeleteView
from .AccountFilterView import AccountFilterView


class AccountDetailWithDeleteView(
    LoginRequiredMixin,
    DetailWithDeleteView,
    CustomActionMixin,
    TestActionMixin,
):
    """View for a single :class:`core.models.Account` instance."""

    URL_NAME = Account.get_detail_web_url_name()
    model = Account
    template_name = "web/account/account_detail.html"
    success_url = reverse_lazy("web:" + AccountFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Account]:
        """Restricts the queryset to objects owned by the requesting user."""
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .prefetch_related("mailboxes")
        )

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended to add the accounts latest emails to the context."""
        context = super().get_context_data(**kwargs)
        context["latest_emails"] = (
            Email.objects.filter(mailbox__account=self.object)
            .order_by("-created")
            .select_related("mailbox", "mailbox__account")[:25]
        )
        return context

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_update_mailboxes(self, request: HttpRequest) -> HttpResponse:
        """Handler function for the `update-mailboxes` action.

        Args:
            request: The action request to handle.

        Returns:
            A template response with the updated view after the action.
        """
        self.object = self.get_object()
        try:
            self.object.update_mailboxes()
        except MailAccountError as error:
            messages.error(
                request,
                _("Updating mailboxes failed\n%(error)s") % {"error": str(error)},
            )
        else:
            messages.success(request, _("Updating mailboxes successful"))
        self.object.refresh_from_db()

        return self.get(request)
