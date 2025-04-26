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

"""Module with the :class:`MailboxUpdateView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.urls import reverse_lazy

from core.models.MailboxModel import MailboxModel
from web.views.mailbox_views.MailboxFilterView import MailboxFilterView
from web.views.UpdateOrDeleteView import UpdateOrDeleteView

from ...forms.mailbox_forms.BaseMailboxForm import BaseMailboxForm


class MailboxUpdateOrDeleteView(LoginRequiredMixin, UpdateOrDeleteView):
    """View for updating or deleting a single :class:`core.models.MailboxModel.MailboxModel` instance."""

    model = MailboxModel
    form_class = BaseMailboxForm
    template_name = "web/mailbox/mailbox_edit.html"
    context_object_name = "mailbox"
    delete_success_url = reverse_lazy("web:" + MailboxFilterView.URL_NAME)
    URL_NAME = MailboxModel.get_edit_web_url_name()

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return MailboxModel.objects.filter(account__user=self.request.user)
