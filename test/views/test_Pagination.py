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
from model_bakery import baker
from test_AccountViewSet import fixture_accountModel

from api.v1.views.EMailViewSet import EMailViewSet
from core.models.EMailModel import EMailModel
from Emailkasten.utils import get_config


@pytest.fixture(name='emails')
def fixture_emails(accountModel):
    """Create a bunch of :class:`core.models.EMailModel.EMailModel`s owned by :attr:`owner_user`.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The email instance for testing.
    """
    return baker.make(EMailModel, account=accountModel, _quantity=25)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page_query, page_size_query',
    [
        (1, 10),
        (2, 5),
        (3, 10)
    ]
)
def test_Pagination(emails, list_url, owner_apiClient, page_query, page_size_query):
    query = {'page': page_query, 'page_size': page_size_query}

    response = owner_apiClient.get(list_url(EMailViewSet), query)

    assert response.data['count'] == len(emails)
    assert len(response.data['results']) == min(page_size_query, len(emails)-(page_query-1)*page_size_query)
    assert min(item['id'] for item in response.data['results']) == (page_query-1)*page_size_query + 1
    assert max(item['id'] for item in response.data['results']) == min((page_query)*page_size_query, len(emails))


@pytest.mark.django_db
def test_Pagination_max(monkeypatch, emails, list_url, owner_apiClient):
    monkeypatch.setattr("api.v1.pagination.Pagination.max_page_size", len(emails)//2)
    query = {'page': 1, 'page_size': len(emails)}

    response = owner_apiClient.get(list_url(EMailViewSet), query)

    assert response.data['count'] == len(emails)
    assert len(response.data['results']) == len(emails)//2
    assert min(item['id'] for item in response.data['results']) == 1
    assert max(item['id'] for item in response.data['results']) == len(emails)//2


@pytest.mark.django_db
def test_Pagination_default(emails, list_url, owner_apiClient):
    response = owner_apiClient.get(list_url(EMailViewSet))

    assert response.data['count'] == len(emails)
    assert len(response.data['results']) == get_config('API_DEFAULT_PAGE_SIZE')
    assert min(item['id'] for item in response.data['results']) == 1
    assert max(item['id'] for item in response.data['results']) == get_config('API_DEFAULT_PAGE_SIZE')
