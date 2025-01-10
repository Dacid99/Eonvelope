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
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.constants.APIConfiguration import DEFAULT_PAGE_SIZE

@pytest.fixture(name='emails')
def fixture_emails(owner_user):
    baker.make(EMailModel, owner_user, _quantity=25)


@pytest.django_db
@pytest.mark.parametrize(
    'page_query, page_size_query, expected_page_number, expected_count',
    [
        (1, 10, 1, 10),
        (2, 5, 2, 5),
        (1, 'all', 1, 25),
        (3, 10, 3, 5)
    ]
)
def test_Pagination(emails, owner_apiClient, page_query, page_size_query, expected_count, expected_page_number):
    query = {'page': page_query, 'page_size': page_size_query}

    response = owner_apiClient.get(list_url(EMailModel), query)

    assert response['count'] == expected_page_number
