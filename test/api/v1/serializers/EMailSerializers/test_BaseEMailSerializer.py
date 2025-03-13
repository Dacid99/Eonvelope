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

"""Test module for :mod:`api.v1.serializers.EMailSerializers.BaseEMailSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.email_serializers.BaseEMailSerializer import BaseEMailSerializer


@pytest.mark.django_db
def test_output(emailModel):
    """Tests for the expected output of the serializer."""
    serializerData = BaseEMailSerializer(instance=emailModel).data

    assert "id" in serializerData
    assert serializerData["id"] == emailModel.id
    assert "message_id" in serializerData
    assert serializerData["message_id"] == emailModel.message_id
    assert "datetime" in serializerData
    assert datetime.fromisoformat(serializerData["datetime"]) == emailModel.datetime
    assert "email_subject" in serializerData
    assert serializerData["email_subject"] == emailModel.email_subject
    assert "plain_bodytext" in serializerData
    assert serializerData["plain_bodytext"] == emailModel.plain_bodytext
    assert "html_bodytext" in serializerData
    assert serializerData["html_bodytext"] == emailModel.html_bodytext
    assert "inReplyTo" in serializerData
    assert serializerData["inReplyTo"] is None
    assert "datasize" in serializerData
    assert serializerData["datasize"] == emailModel.datasize
    assert "is_favorite" in serializerData
    assert serializerData["is_favorite"] == emailModel.is_favorite
    assert "eml_filepath" not in serializerData
    assert "prerender_filepath" not in serializerData
    assert "mailbox" in serializerData
    assert serializerData["mailbox"] == emailModel.mailbox.id
    assert "headers" in serializerData
    assert serializerData["headers"] == emailModel.headers
    assert "x_spam" in serializerData
    assert serializerData["x_spam"] == emailModel.x_spam
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == emailModel.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == emailModel.updated
    assert "attachments" not in serializerData
    assert "mailinglist" in serializerData
    assert serializerData["mailinglist"] == emailModel.mailinglist.id
    assert "correspondents" in serializerData
    assert isinstance(serializerData["correspondents"], list)
    assert len(serializerData["correspondents"]) == 1
    assert isinstance(serializerData["correspondents"][0], int)

    assert len(serializerData) == 16


@pytest.mark.django_db
def test_input(emailModel):
    """Tests for the expected input of the serializer."""
    serializer = BaseEMailSerializer(data=model_to_dict(emailModel))
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
    assert serializerData["is_favorite"] == emailModel.is_favorite
    assert "eml_filepath" not in serializerData
    assert "prerender_filepath" not in serializerData
    assert "mailbox" not in serializerData
    assert "headers" not in serializerData
    assert "x_spam" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert "attachments" not in serializerData
    assert "mailinglist" not in serializerData
    assert "correspondents" not in serializerData

    assert len(serializerData) == 1
