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

"""web.views package containing all views for the Emailkasten webapp."""

from .account_views import (
    AccountCreateView,
    AccountDetailWithDeleteView,
    AccountEmailsFilterView,
    AccountFilterView,
    AccountUpdateOrDeleteView,
)
from .attachment_views import AttachmentDetailWithDeleteView, AttachmentFilterView
from .correspondent_views import (
    CorrespondentDetailWithDeleteView,
    CorrespondentEmailsFilterView,
    CorrespondentFilterView,
    CorrespondentUpdateOrDeleteView,
)
from .daemon_views import (
    DaemonCreateView,
    DaemonDetailWithDeleteView,
    DaemonFilterView,
    DaemonUpdateOrDeleteView,
)
from .DashboardView import DashboardView
from .email_views import (
    EmailArchiveIndexView,
    EmailDayArchiveView,
    EmailDetailWithDeleteView,
    EmailFilterView,
    EmailMonthArchiveView,
    EmailWeekArchiveView,
    EmailYearArchiveView,
)
from .mailbox_views import (
    MailboxDetailWithDeleteView,
    MailboxEmailsFilterView,
    MailboxFilterView,
    MailboxUpdateOrDeleteView,
    UploadEmailView,
)


__all__ = [
    "AccountCreateView",
    "AccountDetailWithDeleteView",
    "AccountEmailsFilterView",
    "AccountFilterView",
    "AccountUpdateOrDeleteView",
    "AttachmentDetailWithDeleteView",
    "AttachmentFilterView",
    "CorrespondentDetailWithDeleteView",
    "CorrespondentEmailsFilterView",
    "CorrespondentFilterView",
    "CorrespondentUpdateOrDeleteView",
    "DaemonCreateView",
    "DaemonDetailWithDeleteView",
    "DaemonFilterView",
    "DaemonUpdateOrDeleteView",
    "DashboardView",
    "EmailArchiveIndexView",
    "EmailDayArchiveView",
    "EmailDetailWithDeleteView",
    "EmailFilterView",
    "EmailMonthArchiveView",
    "EmailWeekArchiveView",
    "EmailYearArchiveView",
    "MailboxDetailWithDeleteView",
    "MailboxEmailsFilterView",
    "MailboxFilterView",
    "MailboxUpdateOrDeleteView",
    "UploadEmailView",
]
