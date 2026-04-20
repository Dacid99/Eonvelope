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

"""Test module for :mod:`core.utils.iterations`."""

from core.utils.iterations import slices


def test_slices(faker):
    """Tests :func:`core.utils.iterations.slices`."""
    start = faker.random.randint(0, 10)
    size = faker.random.randint(1, 20)
    generator = slices(start, size)

    first_item = next(generator)

    assert isinstance(first_item, slice)
    assert first_item.start == start
    assert first_item.stop == start + size
    assert first_item.stop == next(generator).start
    next_item = next(generator)
    assert isinstance(next_item, slice)
    assert next_item.stop - next_item.start == size
    assert next_item.stop == next(generator).start
