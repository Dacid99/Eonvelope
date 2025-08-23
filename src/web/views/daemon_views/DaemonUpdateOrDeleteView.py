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

"""Module with the :class:`web.views.DaemonUpdateView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.urls import reverse_lazy

from core.models import Daemon

from ...forms import BaseDaemonForm
from ..UpdateOrDeleteView import UpdateOrDeleteView
from .DaemonFilterView import DaemonFilterView


class DaemonUpdateOrDeleteView(LoginRequiredMixin, UpdateOrDeleteView):
    """View for updating or deleting a single :class:`core.models.Daemon` instance."""

    model = Daemon
    form_class = BaseDaemonForm
    template_name = "web/daemon/daemon_edit.html"
    delete_success_url = reverse_lazy("web:" + DaemonFilterView.URL_NAME)
    URL_NAME = Daemon.get_edit_web_url_name()

    @override
    def get_queryset(self) -> QuerySet[Daemon]:
        """Restricts the queryset to objects owned by the requesting user."""
        return super().get_queryset().filter(mailbox__account__user=self.request.user)

    @override
    def get_form(
        self, form_class: type[BaseDaemonForm] | None = None
    ) -> BaseDaemonForm:
        form = super().get_form(form_class)
        form.fields["fetching_criterion"].choices = (
            self.object.mailbox.available_fetching_criterion_choices
        )

        return form
