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

"""Test module for the :class:`web.tables.email_tables.BaseEmailTable` class."""

from core.models import Email
from web.tables import BaseEmailTable


def test_output(fake_email):
    """Test the data present in the table."""
    table = BaseEmailTable(Email.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "is_favorite" in fields
    assert "mailbox__account" in fields
    assert "mailbox" in fields
    assert "subject" in fields
    assert "datetime" in fields
    assert "datasize" in fields
    assert "x_spam_flag" in fields
    assert len(fields) == 8
