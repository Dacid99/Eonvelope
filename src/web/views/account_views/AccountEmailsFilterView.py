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

"""Module with the :class:`web.views.AccountEmailsFilterView` view."""

from typing import Any, override

from django.db.models import QuerySet
from django.views.generic.detail import SingleObjectMixin

from core.models import Account, Email
from web.views.email_views import EmailFilterView


class AccountEmailsFilterView(EmailFilterView, SingleObjectMixin):  # type: ignore[misc]  # SingleObjectMixin attributes are shadowed purposefully
    """View for filtering listed :class:`core.models.Email` instances belonging to a certain account."""

    URL_NAME = "account-emails"
    template_name = "web/account/account_email_filter_list.html"

    @override
    def get_queryset(self) -> QuerySet[Email]:
        account_queryset = Account.objects.filter(user=self.request.user)  # type: ignore[misc]  # user auth is checked by LoginRequiredMixin, we also test for this
        self.object = self.get_object(queryset=account_queryset)
        return super().get_queryset().filter(mailbox__account=self.object)

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["account"] = self.object
        return context
