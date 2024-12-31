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
from django.forms.models import model_to_dict

from Emailkasten.Serializers.AccountSerializers.BaseAccountSerializer import \
    BaseAccountSerializer

from ...models.test_AccountModel import fixture_accountModel


@pytest.mark.django_db
def test_output(account):
    serializerData = BaseAccountSerializer(instance=account).data

    assert 'id' in serializerData
    assert 'password' not in serializerData
    assert 'mail_address' in serializerData
    assert 'mail_host' in serializerData
    assert 'mail_host_port' in serializerData
    assert 'protocol' in serializerData
    assert 'timeout' in serializerData
    assert 'is_healthy' in serializerData
    assert 'is_favorite' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData
    assert 'user' not in serializerData
    assert len(serializerData) == 10


@pytest.mark.django_db
def test_input(account):
    serializer = BaseAccountSerializer(data=model_to_dict(account))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'password' in serializerData
    assert 'mail_address' in serializerData
    assert 'mail_host' in serializerData
    assert 'mail_host_port' in serializerData
    assert 'protocol' in serializerData
    assert 'timeout' in serializerData
    assert 'is_healthy' not in serializerData
    assert 'is_favorite' in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert 'user' not in serializerData
    assert len(serializerData) == 7
