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

"""Test module for :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`."""

import pytest

from api.v1.filters.CorrespondentFilterSet import CorrespondentFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_email_name_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.email_name` field.
    """
    query = {"email_name" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_email_address_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.email_address` field.
    """
    query = {"email_address" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_updated_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.CorrespondentFilterSet.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.updated` field.
    """
    query = {"updated" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
