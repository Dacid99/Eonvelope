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

"""Test module for :class:`api.v1.filters.MailboxFilterSet`."""

import pytest

from api.v1.filters import MailboxFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize("searched_field", ["name"])
def test_search_filter(faker, mailbox_queryset, searched_field):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s search filtering."""
    target_text = faker.sentence()
    target_id = faker.random.randint(0, len(mailbox_queryset) - 1)
    mailbox_queryset.filter(id=target_id).update(**{searched_field: target_text})
    query = {"search": target_text[2:10]}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.count() == 1
    assert filtered_data.get().id == target_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_name_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.name` field.
    """
    query = {"name" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_save_to_eml_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.save_to_eml` field.
    """
    query = {"save_to_eml" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_save_attachments_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.save_attachments` field.
    """
    query = {"save_attachments" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

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
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.is_healthy` field.
    """
    query = {"is_healthy" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

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
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_updated_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the :attr:`core.models.Mailbox.Mailbox.updated` field.
    """
    query = {"updated" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

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
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.mail_address` field.
    """
    query = {"account__mail_address" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_account__mail_host_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.mail_host` field.
    """
    query = {"account__mail_host" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_account__is_healthy_filter(
    mailbox_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.MailboxFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.is_healthy` field.
    """
    query = {"account__is_healthy" + lookup_expr: filterquery}

    filtered_data = MailboxFilterSet(query, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
