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

"""web.views package containing all views for the Emailkasten webapp."""

from .account_views import (
    AccountCreateView,
    AccountDetailWithDeleteView,
    AccountEmailsFilterView,
    AccountEmailsTableView,
    AccountFilterView,
    AccountTableView,
    AccountUpdateOrDeleteView,
)
from .attachment_views import (
    AttachmentDetailWithDeleteView,
    AttachmentFilterView,
    AttachmentTableView,
)
from .correspondent_views import (
    CorrespondentDetailWithDeleteView,
    CorrespondentEmailsFilterView,
    CorrespondentEmailsTableView,
    CorrespondentFilterView,
    CorrespondentTableView,
    CorrespondentUpdateOrDeleteView,
)
from .daemon_views import (
    DaemonCreateView,
    DaemonDetailWithDeleteView,
    DaemonFilterView,
    DaemonTableView,
    DaemonUpdateOrDeleteView,
)
from .DashboardView import DashboardView
from .email_views import (
    EmailArchiveIndexView,
    EmailConversationView,
    EmailDayArchiveView,
    EmailDetailWithDeleteView,
    EmailFilterView,
    EmailMonthArchiveView,
    EmailTableView,
    EmailWeekArchiveView,
    EmailYearArchiveView,
)
from .mailbox_views import (
    MailboxCreateDaemonView,
    MailboxDetailWithDeleteView,
    MailboxEmailsFilterView,
    MailboxEmailsTableView,
    MailboxFilterView,
    MailboxTableView,
    MailboxUpdateOrDeleteView,
    UploadEmailView,
)


__all__ = [
    "AccountCreateView",
    "AccountDetailWithDeleteView",
    "AccountEmailsFilterView",
    "AccountEmailsTableView",
    "AccountFilterView",
    "AccountTableView",
    "AccountUpdateOrDeleteView",
    "AttachmentDetailWithDeleteView",
    "AttachmentFilterView",
    "AttachmentTableView",
    "CorrespondentDetailWithDeleteView",
    "CorrespondentEmailsFilterView",
    "CorrespondentEmailsTableView",
    "CorrespondentFilterView",
    "CorrespondentTableView",
    "CorrespondentUpdateOrDeleteView",
    "DaemonCreateView",
    "DaemonDetailWithDeleteView",
    "DaemonFilterView",
    "DaemonTableView",
    "DaemonUpdateOrDeleteView",
    "DashboardView",
    "EmailArchiveIndexView",
    "EmailConversationView",
    "EmailDayArchiveView",
    "EmailDetailWithDeleteView",
    "EmailFilterView",
    "EmailMonthArchiveView",
    "EmailTableView",
    "EmailWeekArchiveView",
    "EmailYearArchiveView",
    "MailboxCreateDaemonView",
    "MailboxDetailWithDeleteView",
    "MailboxEmailsFilterView",
    "MailboxEmailsTableView",
    "MailboxFilterView",
    "MailboxTableView",
    "MailboxUpdateOrDeleteView",
    "UploadEmailView",
]
