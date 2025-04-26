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

"""Test module for :class:`web.filters.MailboxFilter.MailboxFilter`."""

import pytest

from web.filters.MailboxFilter import MailboxFilter

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_name_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.MailboxFilter.MailboxFilter`'s filtering
    for the :attr:`core.models.MailboxModel.MailboxModel.name` field.
    """
    query = {"name" + lookup_expr: filterquery}

    filtered_data = MailboxFilter(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_account__mail_address_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.MailboxFilter.MailboxFilter`'s filtering
    for the :attr:`core.models.MailboxModel.MailboxModel.name` field.
    """
    query = {"account__mail_address" + lookup_expr: filterquery}

    filtered_data = MailboxFilter(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_healthy_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.MailboxFilter.MailboxFilter`'s filtering
    for the :attr:`core.models.MailboxModel.MailboxModel.is_healthy` field.
    """
    query = {"is_healthy" + lookup_expr: filterquery}

    filtered_data = MailboxFilter(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`web.filters.MailboxFilter.MailboxFilter`'s filtering
    for the :attr:`core.models.MailboxModel.MailboxModel.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = MailboxFilter(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`web.filters.MailboxFilter.MailboxFilter`'s filtering
    for the :attr:`core.models.MailboxModel.MailboxModel.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = MailboxFilter(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
