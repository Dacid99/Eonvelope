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

"""Test module for :class:`web.filters.AttachmentFilter.AttachmentFilter`."""

import pytest

from web.filters.AttachmentFilter import AttachmentFilter

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
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_file_name_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the :attr:`core.models.AttachmentModel.AttachmentModel.file_name` field.
    """
    query = {"file_name" + lookup_expr: filterquery}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", CHOICES_TEST_PARAMETERS
)
def test_content_disposition_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the :attr:`core.models.AttachmentModel.AttachmentModel.content_disposition` field.
    """
    query = {"content_disposition": [TEXT_TEST_ITEMS[index] for index in filterquery]}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_content_type_filter(
    attachment_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the :attr:`core.models.AttachmentModel.AttachmentModel.content_type` field.
    """
    query = {"content_type" + lookup_expr: filterquery}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

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
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the :attr:`core.models.AttachmentModel.AttachmentModel.datasize` field.
    """
    query = {"datasize_min": filterquery[0], "datasize_max": filterquery[1]}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

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
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the :attr:`core.models.AttachmentModel.AttachmentModel.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

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
    """Tests :class:`web.filters.AttachmentFilter.AttachmentFilter`'s filtering
    for the related :attr:`core.models.EMailModel.EMailModel.datetime` field.
    """
    query = {"email__datetime" + lookup_expr: filterquery}

    filtered_data = AttachmentFilter(query, queryset=attachment_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
