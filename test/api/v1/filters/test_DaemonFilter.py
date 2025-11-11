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

"""Test module for :class:`api.v1.filters.DaemonFilterSet`."""

import pytest

from api.v1.filters import DaemonFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize("searched_field", ["uuid"])
def test_search_filter(faker, daemon_queryset, searched_field):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s search filtering."""
    target_text = faker.uuid4()
    target_id = faker.random.randint(0, len(daemon_queryset) - 1)
    daemon_queryset.filter(id=target_id).update(**{searched_field: target_text})
    query = {"search": target_text[2:10]}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_interval__every_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.interval` field.
    """
    query = {"interval__every" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_enabled_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.celery_task.enabled` field.
    """
    query = {"enabled" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_celery_task__total_run_count_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.celery_task.enabled` field.
    """
    query = {"celery_task__total_run_count" + lookup_expr: filterquery}

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
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
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
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_last_error_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.last_error` field.
    """
    query = {"last_error" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_last_error_occurred_at_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.last_error_occurred_at` field.
    """
    query = {"last_error_occurred_at" + lookup_expr: filterquery}

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
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_updated_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the :attr:`core.models.Daemon.Daemon.updated` field.
    """
    query = {"updated" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_mailbox__is_healthy_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the related :attr:`core.models.Mailbox.Mailbox.is_healthy` field.
    """
    query = {"mailbox__is_healthy" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mail_address_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the related :attr:`core.models.Daemon.Daemon.mail_address` field.
    """
    query = {"mail_address" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mail_host_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the related :attr:`core.models.Daemon.Daemon.mail_host` field.
    """
    query = {"mail_host" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_account__is_healthy_filter(
    daemon_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.DaemonFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.is_healthy` field.
    """
    query = {"account__is_healthy" + lookup_expr: filterquery}

    filtered_data = DaemonFilterSet(query, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
