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

"""Test module for :class:`web.filters.CorrespondentFilterSet`."""

import pytest

from web.filters import CorrespondentFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "searched_field",
    [
        "email_address",
        "email_name",
        "real_name",
        "list_id",
        "list_owner",
        "list_subscribe",
        "list_unsubscribe",
        "list_unsubscribe_post",
        "list_post",
        "list_help",
        "list_archive",
    ],
)
def test_text_search_filter(faker, correspondent_queryset, searched_field):
    """Tests :class:`web.filters.CorrespondentFilterSet`'s search filtering."""
    target_text = faker.sentence()
    target_id = faker.random.randint(0, len(correspondent_queryset) - 1)
    correspondent_queryset.filter(id=target_id).update(**{searched_field: target_text})
    query = {"text_search": target_text[2:10]}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    correspondent_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.CorrespondentFilterSet`'s filtering
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
    """Tests :class:`web.filters.CorrespondentFilterSet`'s filtering
    for the :attr:`core.models.Correspondent.Correspondent.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = CorrespondentFilterSet(query, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
