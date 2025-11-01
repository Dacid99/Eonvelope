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

"""Test module for the :class:`web.tables.correspondent_tables.BaseCorrespondentTable` class."""

from core.models import EmailCorrespondent
from web.tables import BaseCorrespondentEmailTable


def test_output(fake_emailcorrespondent):
    """Test the data present in the table."""
    table = BaseCorrespondentEmailTable(EmailCorrespondent.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "mention" in fields
    assert "email__is_favorite" in fields
    assert "email__subject" in fields
    assert "email__datetime" in fields
    assert "email__mailbox" in fields
    assert "email__mailbox__account" in fields
    assert "email__x_spam" in fields
    assert "email__datasize" in fields
    assert len(fields) == 9
