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

"""Test module for :class:`web.filters.AttachmentFilterSet`."""

import pytest

from web.filters import AttachmentFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    CHOICES_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
    TEXT_TEST_ITEMS,
)


@pytest.mark.django_db
@pytest.mark.parametrize("searched_field", ["file_name", "content_id"])
def test_search_filter(faker, attachment_queryset, searched_field):
    """Tests :class:`web.filters.AttachmentFilterSet`'s search filtering."""
    target_text = faker.sentence()
    target_id = faker.random.randint(0, len(attachment_queryset) - 1)
    attachment_queryset.filter(id=target_id).update(**{searched_field: target_text})
    query = {"search": target_text[2:10]}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_content_disposition_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the :attr:`core.models.Attachment.Attachment.content_disposition` field.
    """
    query = {"content_disposition": [TEXT_TEST_ITEMS[index] for index in filterquery]}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_content_maintype_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the :attr:`core.models.Attachment.Attachment.content_maintype` field.
    """
    query = {"content_maintype": [TEXT_TEST_ITEMS[index] for index in filterquery]}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_content_subtype_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the :attr:`core.models.Attachment.Attachment.content_subtype` field.
    """
    query = {"content_subtype": [TEXT_TEST_ITEMS[index] for index in filterquery]}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_datasize_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the :attr:`core.models.Attachment.Attachment.datasize` field.
    """
    query = {"datasize_min": filterquery[0], "datasize_max": filterquery[1]}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the :attr:`core.models.Attachment.Attachment.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_email__datetime_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilterSet`'s filtering
    for the related :attr:`core.models.Email.Email.datetime` field.
    """
    query = {"email__datetime" + lookup_expr: filterquery}

    filtered_data = AttachmentFilterSet(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
