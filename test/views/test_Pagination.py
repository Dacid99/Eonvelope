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

from api.v1.views.EMailViewSet import EMailViewSet
from core.models.EMailModel import EMailModel
from Emailkasten.utils import get_config


@pytest.fixture(name="emailBunchCount", autouse=True)
def fixture_emailBunchCount(mailboxModel):
    """Create a bunch of :class:`core.models.EMailModel.EMailModel`s owned by :attr:`owner_user`.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        All emails in the db belonging to `owner_user`.
    """
    baker.make(EMailModel, mailbox=mailboxModel, _quantity=24)
    return EMailModel.objects.filter(
        mailbox__account__user=mailboxModel.account.user
    ).count()


@pytest.mark.django_db
@pytest.mark.parametrize("page_query, page_size_query", [(1, 10), (2, 5), (3, 10)])
def test_Pagination(
    list_url, owner_apiClient, emailBunchCount, page_query, page_size_query
):
    query = {"page": page_query, "page_size": page_size_query}

    response = owner_apiClient.get(list_url(EMailViewSet), query)

    assert response.data["count"] == emailBunchCount
    assert len(response.data["results"]) == min(
        page_size_query, emailBunchCount - (page_query - 1) * page_size_query
    )
    assert (
        min(item["id"] for item in response.data["results"])
        == (page_query - 1) * page_size_query + 1
    )
    assert max(item["id"] for item in response.data["results"]) == min(
        (page_query) * page_size_query, emailBunchCount
    )


@pytest.mark.django_db
def test_Pagination_max(monkeypatch, list_url, owner_apiClient, emailBunchCount):
    monkeypatch.setattr(
        "api.v1.pagination.Pagination.max_page_size", emailBunchCount // 2
    )
    query = {"page": 1, "page_size": emailBunchCount}

    response = owner_apiClient.get(list_url(EMailViewSet), query)

    assert response.data["count"] == emailBunchCount
    assert len(response.data["results"]) == emailBunchCount // 2
    assert min(item["id"] for item in response.data["results"]) == 1
    assert max(item["id"] for item in response.data["results"]) == emailBunchCount // 2


@pytest.mark.django_db
def test_Pagination_default(list_url, owner_apiClient, emailBunchCount):

    response = owner_apiClient.get(list_url(EMailViewSet))

    assert response.data["count"] == emailBunchCount
    assert len(response.data["results"]) == get_config("API_DEFAULT_PAGE_SIZE")
    assert min(item["id"] for item in response.data["results"]) == 1
    assert max(item["id"] for item in response.data["results"]) == get_config(
        "API_DEFAULT_PAGE_SIZE"
    )
