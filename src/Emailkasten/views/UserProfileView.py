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

"""Module with the :class:`web.views.AccountUpdateView` view."""

from typing import override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from Emailkasten.forms import UserProfileForm
from Emailkasten.models import UserProfile


class UserProfileView(LoginRequiredMixin, UpdateView):
    """View for updating the users profile."""

    URL_NAME = "account_profile"
    model = UserProfile
    form_class = UserProfileForm
    success_url = reverse_lazy(URL_NAME)
    template_name = "account/profile.html"

    @override
    def get_object(self, queryset=None) -> UserProfile:
        """Get the requesting users profile."""
        return self.request.user.profile
