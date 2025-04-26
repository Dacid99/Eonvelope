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

"""Test module for :class:`web.filters.DaemonFilter.DaemonFilter`."""

import pytest

from core.constants import EmailFetchingCriterionChoices
from web.filters.DaemonFilter import DaemonFilter

from .conftest import (
    BOOL_TEST_PARAMETERS,
    CHOICES_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_fetching_criterion_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilter.DaemonFilter`'s filtering
    for the :attr:`core.models.AccountModel.AccountModel.fetching_criterion` field.
    """
    query = {
        "fetching_criterion": [
            EmailFetchingCriterionChoices.values[filterquery_item]
            for filterquery_item in filterquery
        ]
    }

    filtered_data = DaemonFilter(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_cycle_interval_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilter.DaemonFilter`'s filtering
    for the :attr:`core.models.DaemonModel.DaemonModel.cycle_interval` field.
    """
    query = {"cycle_interval_min": filterquery[0], "cycle_interval_max": filterquery[1]}

    filtered_data = DaemonFilter(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_healthy_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilter.DaemonFilter`'s filtering
    for the :attr:`core.models.DaemonModel.DaemonModel.is_healthy` field.
    """
    query = {"is_healthy" + lookup_expr: filterquery}

    filtered_data = DaemonFilter(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_running_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilter.DaemonFilter`'s filtering
    for the :attr:`core.models.DaemonModel.DaemonModel.is_running` field.
    """
    query = {"is_running" + lookup_expr: filterquery}

    filtered_data = DaemonFilter(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilter.DaemonFilter`'s filtering
    for the :attr:`core.models.DaemonModel.DaemonModel.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = DaemonFilter(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
