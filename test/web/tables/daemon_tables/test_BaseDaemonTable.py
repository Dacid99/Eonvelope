# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable daemon archiving server
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

"""Test module for the :class:`web.tables.daemon_tables.BaseDaemonTable` class."""

from core.models import Daemon
from web.tables import BaseDaemonTable


def test_output(fake_daemon):
    """Test the data present in the table."""
    table = BaseDaemonTable(Daemon.objects.all())

    values = table.rows
    assert len(values) == 1
    fields = table.columns
    assert "checkbox" in fields
    assert "uuid" in fields
    assert "mailbox" in fields
    assert "fetching_criterion" in fields
    assert "fetching_criterion_arg" in fields
    assert "interval__period" in fields
    assert "interval__every" in fields
    assert "is_healthy" in fields
    assert len(fields) == 8
