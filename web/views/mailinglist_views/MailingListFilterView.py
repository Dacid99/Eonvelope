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

"""Module with the :class:`MailingListFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from core.models import MailingList

from ...filters import MailingListFilterSet
from ..FilterPageView import FilterPageView


class MailingListFilterView(LoginRequiredMixin, FilterPageView):
    """View for filtering listed :class:`core.models.MailingList` instances."""

    URL_NAME = MailingList.get_list_web_url_name()
    model = MailingList
    template_name = "web/mailinglist/mailinglist_filter_list.html"
    context_object_name = "mailinglists"
    filterset_class = MailingListFilterSet
    ordering = ["-created"]

    @override
    def get_queryset(self) -> QuerySet[MailingList]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        return (
            super()
            .get_queryset()
            .filter(emails__mailbox__account__user=self.request.user)
            .distinct()
        )
