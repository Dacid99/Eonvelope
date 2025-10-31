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

"""test.web.tables.mailbox_tables package containing mailbox tables of the Emailkasten webapp."""

from django_tables2 import Column, Table

from core.models import Mailbox
from web.utils.columns import CheckboxColumn


class BaseMailboxTable(Table):
    checkbox = CheckboxColumn()
    name = Column(linkify=True)
    account = Column(
        lambda record: record.account.get_absolute_url(),
        accessor="account__mail_address",
    )

    class Meta:
        model = Mailbox
        fields = (
            "name",
            "account",
            "save_attachments",
            "save_to_eml",
        )
        sequence = ("checkbox", *fields)
