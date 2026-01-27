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

"""web.views.email_views package containing views for the :class:`core.models.Email` data."""

from .archive_views import (
    EmailArchiveIndexView,
    EmailDayArchiveView,
    EmailMonthArchiveView,
    EmailWeekArchiveView,
    EmailYearArchiveView,
)
from .EmailConversationTableView import EmailConversationTableView
from .EmailConversationView import EmailConversationView
from .EmailDetailWithDeleteView import EmailDetailWithDeleteView
from .EmailFilterView import EmailFilterView
from .EmailTableView import EmailTableView

__all__ = [
    "EmailArchiveIndexView",
    "EmailConversationTableView",
    "EmailConversationView",
    "EmailDayArchiveView",
    "EmailDetailWithDeleteView",
    "EmailFilterView",
    "EmailMonthArchiveView",
    "EmailTableView",
    "EmailWeekArchiveView",
    "EmailYearArchiveView",
]
