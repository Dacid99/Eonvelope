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

"""Module with the :class:`MailboxEmailsFilterView` view."""

from typing import Any, override

from django.db.models.query import QuerySet
from django.views.generic.detail import SingleObjectMixin

from core.models.Email import Email
from core.models.Mailbox import Mailbox

from ..email_views.EmailFilterView import EmailFilterView


class MailboxEmailsFilterView(EmailFilterView, SingleObjectMixin):  # type: ignore[misc]  # SingleObjectMixin attributes are shadowed purposefully
    """View for filtering listed :class:`core.models.Email.Email` instances belonging to a certain mailbox."""

    URL_NAME = "mailbox-emails"
    template_name = "web/mailbox/mailbox_email_filter_list.html"

    @override
    def get_queryset(self) -> QuerySet[Email]:
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()
        mailbox_queryset = Mailbox.objects.filter(account__user=self.request.user)
        self.object = self.get_object(queryset=mailbox_queryset)
        return super().get_queryset().filter(mailbox=self.object)

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["mailbox"] = self.object
        return context
