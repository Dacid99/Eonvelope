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

"""Test module for the :mod:`api.utils` module."""

import pytest

from api.utils import csv_query_param_to_typed_list, query_param_list_to_typed_list


@pytest.mark.parametrize(
    "query_param_list, expected_list",
    [
        (["1", "7", "3"], [1, 7, 3]),
        (["3", "4,9", "0"], [3, 4, 9, 0]),
        (["2,1", "0,59"], [2, 1, 0, 59]),
        ([" 6 ,-4"], [6, -4]),
        (["60,"], [60]),
        (["3", "", "71"], [3, 71]),
        ([], []),
    ],
)
def test_query_param_list_to_typed_list(query_param_list, expected_list):
    result = query_param_list_to_typed_list(query_param_list, int)

    assert result == expected_list


@pytest.mark.parametrize(
    "invalid_query_param_list",
    [
        (["1", "abc", "3,4"]),
        (["1g5y", "6"]),
        (["3", "1e2"]),
        (["7.2", "2"]),
        (["tyu,6", "2"]),
    ],
)
def test_query_param_list_to_typed_list_invalid(invalid_query_param_list):
    with pytest.raises(ValueError):
        query_param_list_to_typed_list(invalid_query_param_list, int)


@pytest.mark.parametrize(
    "query_param, expected_list",
    [
        ("1,2", [1, 2]),
        ("2", [2]),
        (" 4, 8 ", [4, 8]),
        ("45,-5748", [45, -5748]),
        ("", []),
        (",", []),
    ],
)
def test_csv_query_param_to_typed_list(query_param, expected_list):
    result = csv_query_param_to_typed_list(query_param, int)

    assert result == expected_list


@pytest.mark.parametrize(
    "invalid_query_param",
    ["xyz", "7dy4", "9.5", "4e5", "tyu,5"],
)
def test_csv_query_param_to_typed_list_invalid(invalid_query_param):
    with pytest.raises(ValueError):
        csv_query_param_to_typed_list(invalid_query_param, int)
