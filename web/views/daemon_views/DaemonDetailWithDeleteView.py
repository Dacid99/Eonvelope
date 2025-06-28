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

"""Module with the :class:`web.views.DaemonDetailWithDeleteView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import DeletionMixin

from core.models import Daemon

from ...mixins.CustomActionMixin import CustomActionMixin
from ..DetailWithDeleteView import DetailWithDeleteView
from .DaemonFilterView import DaemonFilterView


class DaemonDetailWithDeleteView(
    LoginRequiredMixin,
    DetailWithDeleteView,
    CustomActionMixin,
):
    """View for a single :class:`core.models.Daemon` instance."""

    URL_NAME = Daemon.get_detail_web_url_name()
    model = Daemon
    template_name = "web/daemon/daemon_detail.html"
    success_url = reverse_lazy("web:" + DaemonFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[Daemon]:
        """Restricts the queryset to objects owned by the requesting user."""
        return Daemon.objects.filter(  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
            mailbox__account__user=self.request.user
        ).select_related(
            "mailbox", "mailbox__account", "interval", "celery_task"
        )

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if "delete" in request.POST:
            return DeletionMixin.post(self, request)
        return CustomActionMixin.post(self, request)

    def handle_start_daemon(self, request: HttpRequest) -> HttpResponse:
        """Handler function for the `start-daemon` action.

        Args:
            request: The action request to handle.

        Returns:
            A template response with the updated view after the action.
        """
        self.object = self.get_object()
        result = self.object.start()
        self.object.refresh_from_db()
        context = self.get_context_data(object=self.object)
        context["start_result"] = {"status": result}
        return render(request, self.template_name, context)

    def handle_stop_daemon(self, request: HttpRequest) -> HttpResponse:
        """Handler function for the `stop-daemon` action.

        Args:
            request: The action request to handle.

        Returns:
            A template response with the updated view after the action.
        """
        self.object = self.get_object()
        result = self.object.stop()
        self.object.refresh_from_db()
        context = self.get_context_data(object=self.object)
        context["stop_result"] = {"status": result}
        return render(request, self.template_name, context)
