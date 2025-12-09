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

"""The admin module for :mod:`eonvelope`. Registers all models with the admin. Defines a custom admin site."""

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from web.views import DashboardView

from .models import UserProfile


class EonvelopeAdminSite(AdminSite):
    """Customized admin site class for Eonvelope."""

    # Translators: E∘nvelope is the brand name. The ∘ is the ring operator U+2218.
    site_header = _("E∘nvelope Administration")
    # Translators: Eonvelope is the brand name.
    site_title = _("Eonvelope Administration")
    site_url = reverse_lazy("web:" + DashboardView.URL_NAME)
    # Translators: E∘nvelope is the brand name. The ∘ is the ring operator U+2218.
    index_title = _("E∘nvelope Settings")


admin_site = EonvelopeAdminSite()

admin_site.register([UserProfile])

admin.site.register([UserProfile])
