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

"""Module with the :class:`web.views.MailboxFilterView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

from core.models import Mailbox

from ...filters import MailboxFilterSet
from ..FilterPageView import FilterPageView


class MailboxFilterView(LoginRequiredMixin, FilterPageView):
    """View for filtering listed :class:`core.models.Mailbox` instances."""

    URL_NAME = Mailbox.get_list_web_url_name()
    model = Mailbox
    template_name = "web/mailbox/mailbox_filter_list.html"
    context_object_name = "mailboxes"
    filterset_class = MailboxFilterSet
    ordering = ["name"]

    @override
    def get_queryset(self) -> QuerySet[Mailbox]:
        """Restricts the queryset to objects owned by the requesting user."""
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        return (
            super()
            .get_queryset()
            .filter(account__user=self.request.user)
            .select_related("account")
        )
