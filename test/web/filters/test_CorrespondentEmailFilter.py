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

"""Test module for :class:`web.filters.CorrespondentEmailFilterSet`."""

import pytest

from web.filters import CorrespondentEmailFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    CHOICES_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
    TEXT_TEST_ITEMS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "searched_field", ["message_id", "email_subject", "plain_bodytext", "html_bodytext"]
)
def test_text_search_filter(
    faker, emailcorrespondents_queryset, email_queryset, searched_field
):
    """Tests :class:`web.filters.CorrespondentEmailFilterSet`'s search filtering."""
    target_text = faker.sentence()
    target_id = faker.random.randint(0, len(emailcorrespondents_queryset) - 1)
    email_queryset.filter(
        emailcorrespondents=emailcorrespondents_queryset.get(id=target_id)
    ).update(**{searched_field: target_text})
    query = {"text_search": target_text[2:10]}

    filtered_data = CorrespondentEmailFilterSet(
        query, queryset=emailcorrespondents_queryset
    ).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_datetime_filter(
    emailcorrespondents_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.CorrespondentEmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.datetime` field.
    """
    query = {"datetime" + lookup_expr: filterquery}

    filtered_data = CorrespondentEmailFilterSet(
        query, queryset=emailcorrespondents_queryset
    ).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_datasize_filter(
    emailcorrespondents_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.CorrespondentEmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.datasize` field.
    """
    query = {"datasize_min": filterquery[0], "datasize_max": filterquery[1]}

    filtered_data = CorrespondentEmailFilterSet(
        query, queryset=emailcorrespondents_queryset
    ).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    emailcorrespondents_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.CorrespondentEmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = CorrespondentEmailFilterSet(
        query, queryset=emailcorrespondents_queryset
    ).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_x_spam_filter(
    emailcorrespondents_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.x_spam` field.
    """
    query = {"x_spam": [TEXT_TEST_ITEMS[index] for index in filterquery]}

    filtered_data = CorrespondentEmailFilterSet(
        query, queryset=emailcorrespondents_queryset
    ).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
