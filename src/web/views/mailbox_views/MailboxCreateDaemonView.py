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

"""Module with the :class:`web.views.DaemonUpdateView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import BaseFormView

from core.models import Mailbox
from web.forms import CreateMailboxDaemonForm


class MailboxCreateDaemonView(LoginRequiredMixin, DetailView, BaseFormView):
    """View for creating a single :class:`core.models.Daemon` instance."""

    URL_NAME = Mailbox.BASENAME + "-create-daemon"
    model = Mailbox
    form_class = CreateMailboxDaemonForm
    template_name = "web/mailbox/mailbox_daemon_create.html"

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Restricts the queryset to objects owned by the requesting user."""
        return super().get_queryset().filter(account__user=self.request.user)

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object = self.get_object()
        return super().get_context_data(**BaseFormView.get_context_data(self, **kwargs))

    @override
    def get_form_kwargs(self) -> dict[str, Any]:
        """Extended to add the user to the form kwargs."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        form_kwargs["initial"]["mailbox"] = self.get_object().id
        return form_kwargs

    @override
    def get_form(self, form_class: type[CreateMailboxDaemonForm] | None = None) -> Any:
        form = super().get_form(form_class)
        form.fields["fetching_criterion"].choices = (
            self.object.available_fetching_criterion_choices
        )
        return form

    @override
    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    @override
    def form_valid(self, form: CreateMailboxDaemonForm) -> HttpResponse:
        """If the form is valid, save the associated model."""
        form.save()
        return super().form_valid(form)

    @override
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
