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

"""web.views.mailbox_views.MailboxTableView module containing all the mailbox table view for the Emailkasten webapp."""

from django_tables2.views import SingleTableMixin

from web.tables.mailbox_tables.BaseMailboxTable import BaseMailboxTable

from .MailboxFilterView import MailboxFilterView


class MailboxTableView(SingleTableMixin, MailboxFilterView):
    URL_NAME = "mailbox-table"
    template_name = "web/mailbox/mailbox_table.html"
    table_class = BaseMailboxTable
