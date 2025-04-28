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

"""Module with the :class:`EMailDetailWithDeleteView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin

from core.models.EMailModel import EMailModel
from web.views.email_views.EMailFilterView import EMailFilterView


class EMailDetailWithDeleteView(LoginRequiredMixin, DetailView, DeletionMixin):
    """View for a single :class:`core.models.EMailModel.EMailModel` instance."""

    URL_NAME = EMailModel.get_detail_web_url_name()
    model = EMailModel
    template_name = "web/email/email_detail.html"
    context_object_name = "email"
    success_url = reverse_lazy("web:" + EMailFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet[EMailModel]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return EMailModel.objects.none()
        return EMailModel.objects.filter(mailbox__account__user=self.request.user)
