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

"""Module with the :class:`web.views.AttachmentDetailWithDeleteView` view."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import DeletionMixin
from rest_framework import status

from core.models import Attachment
from web.mixins import CustomActionMixin
from web.views.base import DetailWithDeleteView

from .AttachmentFilterView import AttachmentFilterView

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


class AttachmentDetailWithDeleteView(
    LoginRequiredMixin, DetailWithDeleteView, CustomActionMixin
):
    """View for a single :class:`core.models.Attachment` instance."""

    URL_NAME = Attachment.get_detail_web_url_name()
    model = Attachment
    template_name = "web/attachment/attachment_detail.html"
    success_url = reverse_lazy("web:" + AttachmentFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Attachment]:
        """Restricts the queryset to objects owned by the requesting user."""
        return (
            super()
            .get_queryset()
            .filter(email__mailbox__account__user=self.request.user)
            .select_related("email")
        )

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
            if service == "paperless":
                self.object.share_to_paperless()
            elif service == "immich":
                self.object.share_to_immich()
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
