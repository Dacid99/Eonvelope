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

"""Test module for the :class:`web.tables.account_tables.BaseAccountTable` class."""

from core.models import Account
from web.tables import BaseAccountTable


def test_output(fake_account):
    """Test the data present in the table."""
    table = BaseAccountTable(Account.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "is_favorite" in fields
    assert "mail_address" in fields
    assert "mail_host" in fields
    assert "mail_host_port" in fields
    assert "protocol" in fields
    assert "timeout" in fields
    assert "is_healthy" in fields
    assert len(fields) == 8
