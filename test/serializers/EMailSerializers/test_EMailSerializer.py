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

"""Test module for :mod:`api.v1.serializers.EMailSerializers.EMailSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.email_serializers.EMailSerializer import EMailSerializer

from ...models.test_EMailModel import fixture_emailModel


@pytest.mark.django_db
def test_output(email):
    """Tests for the expected output of the serializer."""
    serializerData = EMailSerializer(instance=email).data

    assert "id" in serializerData
    assert serializerData["id"] == email.id
    assert "message_id" in serializerData
    assert serializerData["message_id"] == email.message_id
    assert "datetime" in serializerData
    assert datetime.fromisoformat(serializerData["datetime"]) == email.datetime
    assert "email_subject" in serializerData
    assert serializerData["email_subject"] == email.email_subject
    assert "plain_bodytext" in serializerData
    assert serializerData["plain_bodytext"] == email.plain_bodytext
    assert "html_bodytext" in serializerData
    assert serializerData["html_bodytext"] == email.html_bodytext
    assert "inReplyTo" in serializerData
    assert serializerData["inReplyTo"] is None
    assert "datasize" in serializerData
    assert serializerData["datasize"] == email.datasize
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == email.is_favorite
    assert "mailbox" in serializerData
    assert serializerData["mailbox"] == email.mailbox.id
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == email.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == email.updated
    assert "replies" in serializerData
    assert serializerData["replies"] == []
    assert "attachments" in serializerData
    assert serializerData["attachments"] == []
    assert "mailinglist" in serializerData
    assert serializerData["mailinglist"] is None
    assert "correspondents" in serializerData
    assert serializerData["correspondents"] == []
    assert len(serializerData) == 16


@pytest.mark.django_db
def test_input(email):
    """Tests for the expected input of the serializer."""
    serializer = EMailSerializer(data=model_to_dict(email))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "message_id" not in serializerData
    assert "datetime" not in serializerData
    assert "email_subject" not in serializerData
    assert "plain_bodytext" not in serializerData
    assert "html_bodytext" not in serializerData
    assert "inReplyTo" not in serializerData
    assert "datasize" not in serializerData
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == email.is_favorite
    assert "mailbox" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert "replies" not in serializerData
    assert "attachments" not in serializerData
    assert "mailinglist" not in serializerData
    assert "correspondents" not in serializerData
    assert len(serializerData) == 1
