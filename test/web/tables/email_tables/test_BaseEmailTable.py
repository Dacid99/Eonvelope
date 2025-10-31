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

"""test.web.tables.email_tables module containing tests for the BaseEmailTable class of the Emailkasten webapp."""

from core.models import Email
from web.tables import BaseEmailTable


def test_output(fake_email):
    table = BaseEmailTable(Email.objects.all())

    table_list = list(table.as_values())
    assert len(table_list) == 2
    fields = table.columns
    assert "subject" in fields
    assert "message_id" in fields
    assert "datetime" in fields
    assert "plain_bodytext" in fields
    assert "html_bodytext" in fields
    assert "datasize" in fields
    assert len(fields) == 6
    values = table_list[1]
    assert len(values) == 6
