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

"""Test module for :mod:`api.v1.views.MailboxViewSet`'s basic CRUD actions.

Fixtures:
    :func:`fixture_mailboxPayload`: Creates clean :class:`core.models.MailboxModel.MailboxModel` payload for a patch, post or put request.
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from model_bakery import baker
from rest_framework import status

from api.v1.views.MailboxViewSet import MailboxViewSet
from core.constants import EmailFetchingCriterionChoices
from core.models.DaemonModel import DaemonModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.utils.fetchers.exceptions import MailAccountError, MailboxError


if TYPE_CHECKING:
    from typing import Any


@pytest.fixture
def mailboxPayload(accountModel) -> dict[str, Any]:
    """Creates clean :class:`core.models.MailboxModel.MailboxModel` payload for a patch, post or put request.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The clean payload.
    """
    mailboxData = baker.prepare(
        MailboxModel, account=accountModel, save_attachments=False
    )
    payload = model_to_dict(mailboxData)
    payload.pop("id")
    return {key: value for key, value in payload.items() if value is not None}


@pytest.mark.django_db
def test_list_noauth(noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(mailboxModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_get_auth_other(mailboxModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(mailboxModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == mailboxModel.name


@pytest.mark.django_db
def test_patch_noauth(mailboxModel, noauth_apiClient, mailboxPayload, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments is not mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_patch_auth_other(mailboxModel, other_apiClient, mailboxPayload, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments is not mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_patch_auth_owner(mailboxModel, owner_apiClient, mailboxPayload, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] is False
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments is mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_noauth(mailboxModel, noauth_apiClient, mailboxPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments != mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_auth_other(mailboxModel, other_apiClient, mailboxPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments != mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_auth_owner(mailboxModel, owner_apiClient, mailboxPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(MailboxViewSet, mailboxModel), data=mailboxPayload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] == mailboxPayload["save_attachments"]
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments == mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailboxPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, mailboxPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailboxPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_delete_noauth(mailboxModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailboxModel.refresh_from_db()
    assert mailboxModel.name is not None


@pytest.mark.django_db
def test_delete_auth_other(mailboxModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel.name is not None


@pytest.mark.django_db
def test_delete_auth_owner(mailboxModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(MailboxViewSet, mailboxModel))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(mailboxModel.DoesNotExist):
        mailboxModel.refresh_from_db()
