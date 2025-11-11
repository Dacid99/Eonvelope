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

"""Test module for the :class:`web.tables.attachment_tables.BaseAttachmentTable` class."""

from core.models import Attachment
from web.tables import BaseAttachmentTable


def test_output(fake_attachment):
    """Test the data present in the table."""
    table = BaseAttachmentTable(Attachment.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "is_favorite" in fields
    assert "file_name" in fields
    assert "email" in fields
    assert "content_disposition" in fields
    assert "content_id" in fields
    assert "content_type" in fields
    assert "datasize" in fields
    assert len(fields) == 8
