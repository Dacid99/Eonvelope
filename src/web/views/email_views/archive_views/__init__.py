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

"""web.views.email_views.archive_views package containing archive_views for the :class:`core.models.Email` data."""

from .EmailArchiveIndexView import EmailArchiveIndexView
from .EmailDayArchiveView import EmailDayArchiveView
from .EmailMonthArchiveView import EmailMonthArchiveView
from .EmailWeekArchiveView import EmailWeekArchiveView
from .EmailYearArchiveView import EmailYearArchiveView


__all__ = [
    "EmailArchiveIndexView",
    "EmailDayArchiveView",
    "EmailMonthArchiveView",
    "EmailWeekArchiveView",
    "EmailYearArchiveView",
]
