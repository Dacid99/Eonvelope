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

"""Module with the :class:`AccountCreateView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.views.generic import CreateView

from core.models.AccountModel import AccountModel

from ...forms.account_forms.BaseAccountForm import BaseAccountForm


class AccountCreateView(LoginRequiredMixin, CreateView):
    """View for creating a single :class:`core.models.AccountModel.AccountModel` instance."""

    model = AccountModel
    form_class = BaseAccountForm
    template_name = "web/account/account_create.html"
    URL_NAME = AccountModel.BASENAME + "-create"

    @override
    def get_form(
        self, form_class: type[BaseAccountForm] | None = None
    ) -> BaseAccountForm:
        """Extended method to add the requesting user to the created account."""
        if not self.request.user.is_authenticated:
            raise Http404
        form = super().get_form(form_class)
        form.instance.user = self.request.user
        return form  # type: ignore[no-any-return]  # super().get_form returns the form_class arg or classvar, which are both BaseAccountForm
