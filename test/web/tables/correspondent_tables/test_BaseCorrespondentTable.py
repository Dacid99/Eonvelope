# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable correspondent archiving server
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

"""test.web.tables.correspondent_tables module containing tests for the BaseCorrespondentTable class of the Emailkasten webapp."""

from core.models import Correspondent
from web.tables import BaseCorrespondentTable


def test_output(fake_correspondent):
    table = BaseCorrespondentTable(Correspondent.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "is_favorite" in fields
    assert "email_address" in fields
    assert "email_name" in fields
    assert "real_name" in fields
    assert len(fields) == 5
