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
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

from Emailkasten.Models.MailingListModel import MailingListModel
from Emailkasten.Views.MailingListViewSet import MailingListViewSet


@pytest.fixture(name='noauth_apiClient')
def fixture_noauth_apiClient():
    return APIClient()

@pytest.fixture(name='owner_apiClient')
def fixture_owner_apiClient(noauth_apiClient, owner_user):
    return noauth_apiClient.force_authenticate(user=owner_user)

@pytest.fixture(name='other_apiClient')
def fixture_other_apiClient(noauth_apiClient, other_user):
    return noauth_apiClient.force_authenticate(user=other_user)

@pytest.fixture(name='mailingListModel')
def fixture_MailingListModel(owner_user):
    return baker.make(MailingListModel, correspondent__emails__account__user=owner_user)


@pytest.mark.django_db
def test_access_noauth(noauth_apiClient, mailingListModel):
    url = reverse(f'{MailingListViewSet.BASENAME}-list')
    response = noauth_apiClient.get(url)
    assert len(response.data) == 1
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_access_other(other_apiClient, mailingListModel):
    url = reverse(f'{MailingListViewSet.BASENAME}-list')
    response = other_apiClient.get(url)
    assert len(response.data) == 1
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_access_auth(owner_apiClient, mailingListModel):
    url = reverse(f'{MailingListViewSet.BASENAME}-list')
    response = owner_apiClient.get(url)
    assert len(response.data) == 1
    assert response.status_code == status.HTTP_200_OK
