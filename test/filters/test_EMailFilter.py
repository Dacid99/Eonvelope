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

from Emailkasten.Filters.EMailFilter import EMailFilter

from .conftest import ( BOOL_TEST_PARAMETERS,
                        DATETIME_TEST_PARAMETERS,
                        INT_TEST_PARAMETERS,
                       TEXT_TEST_PARAMETERS)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_message_id_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'message_id'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_datetime_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'datetime'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_email_subject_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'email_subject'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_bodytext_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'bodytext'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', INT_TEST_PARAMETERS
)
def test_datasize_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'datasize'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_favorite'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_comments_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'comments'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_keywords_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'keywords'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_importance_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'importance'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_priority_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'priority'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_precedence_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'precedence'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_received_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'received'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_user_agent_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'user_agent'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_auto_submitted_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'auto_submitted'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_type_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_type'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_language_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_language'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_location_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_location'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_priority_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_priority'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_originated_client_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_originated_client'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_spam_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_spam'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_created_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'created'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_updated_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'updated'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_address_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_address'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_host_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_host'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_id_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'mailinglist__list_id'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_owner_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'mailinglist__list_owner'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_correspondents__email_name_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'correspondents__email_name'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_correspondents__email_address_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'correspondents__email_address'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
