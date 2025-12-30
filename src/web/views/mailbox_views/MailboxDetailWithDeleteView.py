# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the :class:`web.views.MailboxDetailWithDeleteView` view."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import DeletionMixin

from core.constants import EmailFetchingCriterionChoices
from core.models import Email, Mailbox
from core.utils.fetchers.exceptions import FetcherError
from web.mixins.CustomActionMixin import CustomActionMixin
from web.mixins.TestActionMixin import TestActionMixin
from web.views.base import DetailWithDeleteView

from .MailboxFilterView import MailboxFilterView


if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest, HttpResponse


class MailboxDetailWithDeleteView(
    LoginRequiredMixin,
    DetailWithDeleteView,
    CustomActionMixin,
    TestActionMixin,
):
    """View for a single :class:`core.models.Mailbox` instance."""

    URL_NAME = Mailbox.get_detail_web_url_name()
    model = Mailbox
    template_name = "web/mailbox/mailbox_detail.html"
    success_url = reverse_lazy("web:" + MailboxFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Restricts the queryset to objects owned by the requesting user."""
        return (
            super()
            .get_queryset()
            .filter(account__user=self.request.user)
            .select_related("account")
            .prefetch_related("daemons")
        )

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended to add the mailboxes latest emails to the context."""
        context = super().get_context_data(**kwargs)
        context["latest_emails"] = (
            Email.objects.filter(mailbox=self.object)
            .select_related("mailbox", "mailbox__account")
            .order_by("-created")[:25]
        )
        return context

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_fetch(self, request: HttpRequest) -> HttpResponse:
        """Handler function for the `fetch` action.

        Args:
            request: The action request to handle.

        Returns:
            A template response with the updated view after the action.
        """
        self.object = self.get_object()
        criterion = request.POST.get("fetch") or EmailFetchingCriterionChoices.ALL.value
        if criterion not in self.object.available_no_arg_fetching_criteria:
            messages.warning(
                request,
                _(
                    "The chosen criterion %(criterion)s is not available for this mailbox."
                )
                % {"criterion": criterion},
            )
            return self.get(request)
        try:
            self.object.fetch(criterion)
        except FetcherError as error:
            messages.error(
                request, _("Fetching failed: %(error)s") % {"error": str(error)}
            )
        else:
            messages.success(request, _("Fetching successful"))
        self.object.refresh_from_db()
        return self.get(request)
