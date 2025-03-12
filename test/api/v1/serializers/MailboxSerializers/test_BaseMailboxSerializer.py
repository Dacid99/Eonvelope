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

"""Test module for :mod:`api.v1.serializers.MailboxSerializers.BaseMailboxSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.mailbox_serializers.BaseMailboxSerializer import (
    BaseMailboxSerializer,
)
from test.core.conftest import mailboxModel


@pytest.mark.django_db
def test_output(mailboxModel):
    """Tests for the expected output of the serializer."""
    serializerData = BaseMailboxSerializer(instance=mailboxModel).data

    assert "id" in serializerData
    assert serializerData["id"] == mailboxModel.id
    assert "name" in serializerData
    assert serializerData["name"] == mailboxModel.name
    assert "account" in serializerData
    assert serializerData["account"] == mailboxModel.account.id
    assert "save_attachments" in serializerData
    assert serializerData["save_attachments"] == mailboxModel.save_attachments
    assert "save_toEML" in serializerData
    assert serializerData["save_toEML"] == mailboxModel.save_toEML
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == mailboxModel.is_favorite
    assert "is_healthy" in serializerData
    assert serializerData["is_healthy"] == mailboxModel.is_healthy
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == mailboxModel.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == mailboxModel.updated
    assert len(serializerData) == 9


@pytest.mark.django_db
def test_input(mailboxModel):
    """Tests for the expected input of the serializer."""
    serializer = BaseMailboxSerializer(data=model_to_dict(mailboxModel))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "name" not in serializerData
    assert "account" not in serializerData
    assert "save_attachments" in serializerData
    assert serializerData["save_attachments"] == mailboxModel.save_attachments
    assert "save_toEML" in serializerData
    assert serializerData["save_toEML"] == mailboxModel.save_toEML
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == mailboxModel.is_favorite
    assert "is_healthy" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 3
