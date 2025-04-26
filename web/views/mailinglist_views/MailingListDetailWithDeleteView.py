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

"""Module with the :class:`MailingListDetailWithDeleteView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import DeletionMixin

from core.models.MailingListModel import MailingListModel
from web.views.mailinglist_views.MailingListFilterView import MailingListFilterView


class MailingListDetailWithDeleteView(LoginRequiredMixin, DetailView, DeletionMixin):
    """View for a single :class:`core.models.MailingListModel.MailingListModel` instance."""

    URL_NAME = MailingListModel.get_detail_web_url_name()
    model = MailingListModel
    template_name = "web/mailinglist/mailinglist_detail.html"
    context_object_name = "mailinglist"
    success_url = reverse_lazy("web:" + MailingListFilterView.URL_NAME)

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return MailingListModel.objects.filter(
            emails__mailbox__account__user=self.request.user
        ).distinct()
