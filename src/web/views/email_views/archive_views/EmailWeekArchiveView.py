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

""":mod:`web.views.email_views.archive_views.EmailWeekArchiveView` module with the EmailWeekArchiveView view."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.dates import WeekArchiveView

from .EmailArchiveMixin import EmailArchiveMixin


class EmailWeekArchiveView(LoginRequiredMixin, EmailArchiveMixin, WeekArchiveView):
    """WeekArchiveView for emails."""

    URL_NAME = EmailArchiveMixin.BASE_URL_NAME + "-week"
    template_name = EmailArchiveMixin.BASE_TEMPLATE_NAME + "week.html"
    week_format = "%W"
