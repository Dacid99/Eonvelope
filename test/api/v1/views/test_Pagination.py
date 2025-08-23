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

import pytest
from model_bakery import baker

from api.v1.views import EmailViewSet
from core.models import Email
from Emailkasten.utils.workarounds import get_config


@pytest.fixture(autouse=True)
def email_bunch_count(fake_mailbox):
    """Create a bunch of :class:`core.models.Email`s owned by :attr:`owner_user`.

    Returns:
        All emails in the db belonging to `owner_user`.
    """
    baker.make(Email, mailbox=fake_mailbox, _quantity=24)
    return Email.objects.filter(
        mailbox__account__user=fake_mailbox.account.user
    ).count()


@pytest.mark.django_db
@pytest.mark.parametrize("page_query, page_size_query", [(1, 10), (2, 5), (3, 10)])
def test_Pagination(
    list_url, owner_api_client, email_bunch_count, page_query, page_size_query
):
    query = {"page": page_query, "page_size": page_size_query}

    response = owner_api_client.get(list_url(EmailViewSet), query)

    assert response.data["count"] == email_bunch_count
    assert len(response.data["results"]) == min(
        page_size_query, email_bunch_count - (page_query - 1) * page_size_query
    )
    assert (
        min(item["id"] for item in response.data["results"])
        == (page_query - 1) * page_size_query + 1
    )
    assert max(item["id"] for item in response.data["results"]) == min(
        (page_query) * page_size_query, email_bunch_count
    )


@pytest.mark.django_db
def test_Pagination_max(monkeypatch, list_url, owner_api_client, email_bunch_count):
    monkeypatch.setattr(
        "api.v1.pagination.Pagination.max_page_size", email_bunch_count // 2
    )
    query = {"page": 1, "page_size": email_bunch_count}

    response = owner_api_client.get(list_url(EmailViewSet), query)

    assert response.data["count"] == email_bunch_count
    assert len(response.data["results"]) == email_bunch_count // 2
    assert min(item["id"] for item in response.data["results"]) == 1
    assert (
        max(item["id"] for item in response.data["results"]) == email_bunch_count // 2
    )


@pytest.mark.django_db
def test_Pagination_default(list_url, owner_api_client, email_bunch_count):

    response = owner_api_client.get(list_url(EmailViewSet))

    assert response.data["count"] == email_bunch_count
    assert len(response.data["results"]) == get_config("API_DEFAULT_PAGE_SIZE")
    assert min(item["id"] for item in response.data["results"]) == 1
    assert max(item["id"] for item in response.data["results"]) == get_config(
        "API_DEFAULT_PAGE_SIZE"
    )
