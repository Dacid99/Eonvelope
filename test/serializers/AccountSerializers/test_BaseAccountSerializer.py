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

"""Test module for :mod:`api.v1.serializers.AccountSerializers.BaseAccountSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.account_serializers.BaseAccountSerializer import \
    BaseAccountSerializer

from ...models.test_AccountModel import fixture_accountModel


@pytest.mark.django_db
def test_output(account):
    """Tests for the expected output of the serializer."""
    serializerData = BaseAccountSerializer(instance=account).data

    assert 'id' in serializerData
    assert serializerData['id'] == account.id
    assert 'password' not in serializerData
    assert 'mail_address' in serializerData
    assert serializerData['mail_address'] == account.mail_address
    assert 'mail_host' in serializerData
    assert serializerData['mail_host'] == account.mail_host
    assert 'mail_host_port' in serializerData
    assert serializerData['mail_host_port'] == account.mail_host_port
    assert 'protocol' in serializerData
    assert serializerData['protocol'] == account.protocol
    assert 'timeout' in serializerData
    assert serializerData['timeout'] == account.timeout
    assert 'is_healthy' in serializerData
    assert serializerData['is_healthy'] == account.is_healthy
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == account.is_favorite
    assert 'created' in serializerData

    assert 'updated' in serializerData

    assert 'user' not in serializerData
    assert len(serializerData) == 10


@pytest.mark.django_db
def test_input(account):
    """Tests for the expected input of the serializer."""
    serializer = BaseAccountSerializer(data=model_to_dict(account))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'password' in serializerData
    assert serializerData['password'] == account.password
    assert 'mail_address' in serializerData
    assert serializerData['mail_address'] == account.mail_address
    assert 'mail_host' in serializerData
    assert serializerData['mail_host'] == account.mail_host
    assert 'mail_host_port' in serializerData
    assert serializerData['mail_host_port'] == account.mail_host_port
    assert 'protocol' in serializerData
    assert serializerData['protocol'] == account.protocol
    assert 'timeout' in serializerData
    assert serializerData['timeout'] == account.timeout
    assert 'is_healthy' not in serializerData
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == account.is_favorite
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert 'user' not in serializerData
    assert len(serializerData) == 7
