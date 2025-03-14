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

"""Test module for :mod:`api.v1.serializers.AccountSerializers.AccountSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.account_serializers.AccountSerializer import AccountSerializer


@pytest.mark.django_db
def test_output(accountModel, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = AccountSerializer(
        instance=accountModel, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == accountModel.id
    assert "password" not in serializerData
    assert "mail_address" in serializerData
    assert serializerData["mail_address"] == accountModel.mail_address
    assert "mailboxes" in serializerData
    assert isinstance(serializerData["mailboxes"], list)
    assert len(serializerData["mailboxes"]) == 1
    assert isinstance(serializerData["mailboxes"][0], dict)
    assert "mail_host" in serializerData
    assert serializerData["mail_host"] == accountModel.mail_host
    assert "mail_host_port" in serializerData
    assert serializerData["mail_host_port"] == accountModel.mail_host_port
    assert "protocol" in serializerData
    assert serializerData["protocol"] == accountModel.protocol
    assert "timeout" in serializerData
    assert serializerData["timeout"] == accountModel.timeout
    assert "is_healthy" in serializerData
    assert serializerData["is_healthy"] == accountModel.is_healthy
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == accountModel.is_favorite
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == accountModel.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == accountModel.updated
    assert "user" not in serializerData
    assert len(serializerData) == 11


@pytest.mark.django_db
def test_input(accountModel, request_context):
    """Tests for the expected input of the serializer."""
    serializer = AccountSerializer(
        data=model_to_dict(accountModel), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "password" in serializerData
    assert serializerData["password"] == accountModel.password
    assert "mail_address" in serializerData
    assert serializerData["mail_address"] == accountModel.mail_address
    assert "mailboxes" not in serializerData
    assert "mail_host" in serializerData
    assert serializerData["mail_host"] == accountModel.mail_host
    assert "mail_host_port" in serializerData
    assert serializerData["mail_host_port"] == accountModel.mail_host_port
    assert "protocol" in serializerData
    assert serializerData["protocol"] == accountModel.protocol
    assert "timeout" in serializerData
    assert serializerData["timeout"] == accountModel.timeout
    assert "is_healthy" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == accountModel.is_favorite
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert "user" not in serializerData
    assert len(serializerData) == 7
