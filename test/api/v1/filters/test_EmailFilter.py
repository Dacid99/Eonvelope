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

"""Test module for :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`."""

import pytest

from api.v1.filters.EmailFilterSet import EmailFilterSet

from .conftest import (
    BOOL_TEST_PARAMETERS,
    DATETIME_TEST_PARAMETERS,
    INT_TEST_PARAMETERS,
    TEXT_TEST_PARAMETERS,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_message_id_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.message_id` field.
    """
    query = {"message_id" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_datetime_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.datetime` field.
    """
    query = {"datetime" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_email_subject_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.email_subject` field.
    """
    query = {"email_subject" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_plain_bodytext_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.plain_bodytext` field.
    """
    query = {"plain_bodytext" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_html_bodytext_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.html_bodytext` field.
    """
    query = {"html_bodytext" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", INT_TEST_PARAMETERS
)
def test_datasize_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.datasize` field.
    """
    query = {"datasize" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.is_favorite` field.
    """
    query = {"is_favorite" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     "lookup_expr, filterquery, expected_indices", JSON_TEST_PARAMETERS
# )
# def test_headers_filter(email_queryset, lookup_expr, filterquery, expected_indices):
#     query = {"headers" + lookup_expr: filterquery}

#     filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

#     assert filtered_data.distinct().count() == filtered_data.count()
#     assert filtered_data.count() == len(expected_indices)
#     for data in filtered_data:
#         assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_x_spam_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.x_spam` field.
    """
    query = {"x_spam" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_created_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.created` field.
    """
    query = {"created" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", DATETIME_TEST_PARAMETERS
)
def test_updated_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the :attr:`core.models.Email.Email.updated` field.
    """
    query = {"updated" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mailbox__name_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.Mailbox.Mailbox.name` field.
    """
    query = {"mailbox__name" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mailbox__account__mail_address_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.mail_address` field.
    """
    query = {"mailbox__account__mail_address" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mailbox__account__mail_host_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.Account.Account.mail_host` field.
    """
    query = {"mailbox__account__mail_host" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_id_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.MailingList.MailingList.list_id` field.
    """
    query = {"mailinglist__list_id" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_owner_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.MailingList.MailingList.list_owner` field.
    """
    query = {"mailinglist__list_owner" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_correspondents__email_name_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.Correspondent.Correspondent.email_name` field.
    """
    query = {"correspondents__email_name" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    "lookup_expr, filterquery, expected_indices", TEXT_TEST_PARAMETERS
)
def test_correspondents__email_address_filter(
    email_queryset, lookup_expr, filterquery, expected_indices
):
    """Tests :class:`api.v1.filters.EmailFilterSet.EmailFilterSet`'s filtering
    for the related :attr:`core.models.Correspondent.Correspondent.email_address` field.
    """
    query = {"correspondents__email_address" + lookup_expr: filterquery}

    filtered_data = EmailFilterSet(query, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
