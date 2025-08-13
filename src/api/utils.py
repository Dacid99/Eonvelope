# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
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

"""Module with utils for the Emailkasten :mod:`api` api."""

type T = type


def query_param_list_to_typed_list(
    query_param_list: list[str], parse_type: T = str
) -> list[T]:
    """Helper function to parse a query_param list
    as returned by :func:`django.utils.datastructures.MultiValueDict.getlist`
    into a typed list.

    This validates the parameters and allows to support the comma-separated query_param format.

    Args:
        query_param_list: List of query parameters to parse.
        parse_type: The type to parse the values to.

    Returns:
        The parsed query parameters in a list of given type.

    Raises:
        ValueError: If one of the parameters cannot be parsed to the given type.
    """
    typed_list: list[T] = []
    try:
        for query_param in query_param_list:
            if query_param:
                typed_list.extend(
                    csv_query_param_to_typed_list(query_param, parse_type)
                )
    except ValueError as e:
        raise ValueError(
            f"Invalid input: expected list of {parse_type.__name__}s or comma-separated {parse_type.__name__}s, got '{query_param}'"
        ) from e
    return typed_list


def csv_query_param_to_typed_list(query_param: str, parse_type: T = str) -> list[T]:
    """Helper function to parse a query_param in csv format into a typed list.

    A string without , also qualifies as csv and is valid input.

    Args:
        query_param: The query parameter to parse.
        parse_type: The type to parse the values to.

    Returns:
        The parsed query parameters in a list of given type.

    Raises:
        ValueError: If one of the parameters in the csv cannot be parsed to the given type.
    """
    try:
        return [parse_type(part.strip()) for part in query_param.split(",") if part]
    except ValueError as e:
        raise ValueError(
            f"Invalid input: expected comma-separated {parse_type.__name__}s, got '{query_param}'"
        ) from e
