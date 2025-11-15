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

"""Test module for :class:`web.filters.DaemonFilterSet`."""

import pytest
from django_celery_beat.models import IntervalSchedule

from core.constants import EmailFetchingCriterionChoices
from web.filters import DaemonFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    CHOICES_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize("searched_field", ["uuid"])
def test_search_filter(faker, daemon_queryset, searched_field):
    """Tests :class:`web.filters.DaemonFilterSet`'s search filtering."""
    target_text = faker.uuid4()
    target_id = faker.random.randint(0, len(daemon_queryset) - 1)
    daemon_queryset.filter(id=target_id).update(**{searched_field: target_text})
    query = {"search": target_text[2:10]}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_fetching_criterion_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Account.Account.fetching_criterion` field.
    """
    query = {
        "fetching_criterion": [
            EmailFetchingCriterionChoices.values[filterquery_item]
            for filterquery_item in filterquery
        ]
    }

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_interval__every_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.interval` field.
    """
    query = {
        "interval__every_min": filterquery[0],
        "interval__every_max": filterquery[1],
    }

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_interval__period_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.interval` field.
    """
    query = {
        "interval__period": [
            IntervalSchedule.PERIOD_CHOICES[filterquery_item][0]
            for filterquery_item in filterquery
        ]
    }

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_celery_task__enabled_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.celery_task.enabled` field.
    """
    query = {"celery_task__enabled" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_healthy_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.is_healthy` field.
    """
    query = {"is_healthy" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
