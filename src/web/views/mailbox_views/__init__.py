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

"""web.views.mailbox_views package containing views for the :class:`core.models.Mailbox` data."""

from .MailboxCreateDaemonView import MailboxCreateDaemonView
from .MailboxDetailWithDeleteView import MailboxDetailWithDeleteView
from .MailboxEmailsFilterView import MailboxEmailsFilterView
from .MailboxEmailsTableView import MailboxEmailsTableView
from .MailboxFilterView import MailboxFilterView
from .MailboxTableView import MailboxTableView
from .MailboxUpdateOrDeleteView import MailboxUpdateOrDeleteView
from .UploadEmailView import UploadEmailView


__all__ = [
    "MailboxCreateDaemonView",
    "MailboxDetailWithDeleteView",
    "MailboxEmailsFilterView",
    "MailboxEmailsTableView",
    "MailboxFilterView",
    "MailboxTableView",
    "MailboxUpdateOrDeleteView",
    "UploadEmailView",
]
