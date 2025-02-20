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

import pytest

from api.v1.filters.MailingListFilter import MailingListFilter

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_id_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_id" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_owner_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_owner" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_subscribe_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_subscribe" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_unsubscribe_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_unsubscribe" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_post_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_post" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_help_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_help" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_list_archive_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"list_archive" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"created" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_updated_filter(
    mailinglist_queryset, lookup_expr, filterquery, expected_indices
):
    query = {"updated" + lookup_expr: filterquery}

    filtered_data = MailingListFilter(query, queryset=mailinglist_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
