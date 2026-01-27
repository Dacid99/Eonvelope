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

"""Module with the :class:`web.views.CorrespondentDetailWithDeleteView` view."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import DeletionMixin
from rest_framework import status

from core.models import Correspondent, EmailCorrespondent
from web.mixins import CustomActionMixin
from web.views.base import DetailWithDeleteView

from .CorrespondentFilterView import CorrespondentFilterView

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class CorrespondentDetailWithDeleteView(
    LoginRequiredMixin, DetailWithDeleteView, CustomActionMixin
):
    """View for a single :class:`core.models.Correspondent` instance."""

    URL_NAME = Correspondent.get_detail_web_url_name()
    model = Correspondent
    template_name = "web/correspondent/correspondent_detail.html"
    success_url = reverse_lazy("web:" + CorrespondentFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Correspondent]:
        """Restricts the queryset to objects owned by the requesting user."""
        return super().get_queryset().filter(user=self.request.user).distinct()

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended to add the accounts latest emails to the context."""
        context = super().get_context_data(**kwargs)
        context["latest_correspondentemails"] = (
            EmailCorrespondent.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
                email__mailbox__account__user=self.request.user,
                correspondent=self.object,
            )
            .select_related("email")
            .order_by("-created")
            .distinct()[:25]
        )
        return context

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_share(self, request: HttpRequest) -> HttpResponse:
        """Handler function for the `share` action.

        Args:
            request: The action request to handle.

        Returns:
            A template response with the updated view after the action.
        """
        self.object = self.get_object()
        service = request.POST.get("share")
        try:
            if service == "nextcloud":
                self.object.share_to_nextcloud()
            else:
                return HttpResponse(status=status.HTTP_204_NO_CONTENT)
        except (
            FileNotFoundError,
            ConnectionError,
            PermissionError,
            ValueError,
            RuntimeError,
        ) as error:
            messages.error(request, str(error))
        else:
            messages.success(request, _("Sharing successful"))

        return self.get(request)
