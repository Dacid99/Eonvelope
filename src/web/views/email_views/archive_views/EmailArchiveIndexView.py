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

""":mod:`web.views.email_views.archive_views.EmailArchiveIndexView` module with the EmailArchiveIndexView view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic.dates import ArchiveIndexView

from .EmailArchiveMixin import EmailArchiveMixin


class EmailArchiveIndexView(LoginRequiredMixin, EmailArchiveMixin, ArchiveIndexView):
    """IndexView for the ArchiveViews for emails."""

    URL_NAME = EmailArchiveMixin.BASE_URL_NAME + "-index"
    template_name = EmailArchiveMixin.BASE_TEMPLATE_NAME + "index.html"
    context_object_name = "object_list"

    @override
    def get_context_data(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(*args, **kwargs)
        context["today"] = timezone.now()
        return context
