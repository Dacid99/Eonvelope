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

"""Test module for :mod:`api.v1.serializers.EmailSerializers.BaseEmailSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.email_serializers.BaseEmailSerializer import BaseEmailSerializer


@pytest.mark.django_db
def test_output(fake_email, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = BaseEmailSerializer(
        instance=fake_email, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == fake_email.id
    assert "message_id" in serializerData
    assert serializerData["message_id"] == fake_email.message_id
    assert "datetime" in serializerData
    assert datetime.fromisoformat(serializerData["datetime"]) == fake_email.datetime
    assert "email_subject" in serializerData
    assert serializerData["email_subject"] == fake_email.email_subject
    assert "plain_bodytext" in serializerData
    assert serializerData["plain_bodytext"] == fake_email.plain_bodytext
    assert "html_bodytext" in serializerData
    assert serializerData["html_bodytext"] == fake_email.html_bodytext
    assert "inReplyTo" in serializerData
    assert serializerData["inReplyTo"] is None
    assert "datasize" in serializerData
    assert serializerData["datasize"] == fake_email.datasize
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == fake_email.is_favorite
    assert "eml_filepath" not in serializerData
    assert "html_filepath" not in serializerData
    assert "mailbox" in serializerData
    assert serializerData["mailbox"] == fake_email.mailbox.id
    assert "headers" in serializerData
    assert serializerData["headers"] == fake_email.headers
    assert "x_spam" in serializerData
    assert serializerData["x_spam"] == fake_email.x_spam
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == fake_email.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == fake_email.updated
    assert "attachments" not in serializerData
    assert "mailinglist" in serializerData
    assert serializerData["mailinglist"] == fake_email.mailinglist.id
    assert "correspondents" in serializerData
    assert isinstance(serializerData["correspondents"], list)
    assert len(serializerData["correspondents"]) == 1
    assert isinstance(serializerData["correspondents"][0], int)

    assert len(serializerData) == 16


@pytest.mark.django_db
def test_input(fake_email, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseEmailSerializer(
        data=model_to_dict(fake_email), context=request_context
    )
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
    assert serializerData["is_favorite"] == fake_email.is_favorite
    assert "eml_filepath" not in serializerData
    assert "html_filepath" not in serializerData
    assert "mailbox" not in serializerData
    assert "headers" not in serializerData
    assert "x_spam" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert "attachments" not in serializerData
    assert "mailinglist" not in serializerData
    assert "correspondents" not in serializerData

    assert len(serializerData) == 1
