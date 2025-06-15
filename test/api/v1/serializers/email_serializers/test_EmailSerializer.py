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

"""Test module for :mod:`api.v1.serializers.EmailSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers import EmailSerializer


@pytest.mark.django_db
def test_output(fake_email, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = EmailSerializer(instance=fake_email, context=request_context).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_email.id
    assert "message_id" in serializer_data
    assert serializer_data["message_id"] == fake_email.message_id
    assert "datetime" in serializer_data
    assert datetime.fromisoformat(serializer_data["datetime"]) == fake_email.datetime
    assert "email_subject" in serializer_data
    assert serializer_data["email_subject"] == fake_email.email_subject
    assert "plain_bodytext" in serializer_data
    assert serializer_data["plain_bodytext"] == fake_email.plain_bodytext
    assert "html_bodytext" in serializer_data
    assert serializer_data["html_bodytext"] == fake_email.html_bodytext
    assert "in_reply_to" in serializer_data
    assert isinstance(serializer_data["in_reply_to"], list)
    assert len(serializer_data["in_reply_to"]) == 0
    assert "references" in serializer_data
    assert isinstance(serializer_data["references"], list)
    assert len(serializer_data["references"]) == 0
    assert "referenced_by" in serializer_data
    assert isinstance(serializer_data["referenced_by"], list)
    assert len(serializer_data["referenced_by"]) == 0
    assert "datasize" in serializer_data
    assert serializer_data["datasize"] == fake_email.datasize
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_email.is_favorite
    assert "eml_filepath" not in serializer_data
    assert "html_version" in serializer_data
    assert "mailbox" in serializer_data
    assert serializer_data["mailbox"] == fake_email.mailbox.id
    assert "headers" not in serializer_data
    assert "x_spam" in serializer_data
    assert serializer_data["x_spam"] == fake_email.x_spam
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_email.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_email.updated
    assert "replies" in serializer_data
    assert serializer_data["replies"] == []
    assert "attachments" in serializer_data
    assert isinstance(serializer_data["attachments"], list)
    assert len(serializer_data["attachments"]) == 1
    assert isinstance(serializer_data["attachments"][0], dict)
    assert "correspondents" in serializer_data
    assert isinstance(serializer_data["correspondents"], list)
    assert len(serializer_data["correspondents"]) == 1
    assert isinstance(serializer_data["correspondents"][0], dict)
    assert len(serializer_data) == 19


@pytest.mark.django_db
def test_input(fake_email, request_context):
    """Tests for the expected input of the serializer."""
    serializer = EmailSerializer(
        data=model_to_dict(fake_email), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "message_id" not in serializer_data
    assert "datetime" not in serializer_data
    assert "email_subject" not in serializer_data
    assert "plain_bodytext" not in serializer_data
    assert "html_bodytext" not in serializer_data
    assert "in_reply_to" not in serializer_data
    assert "references" not in serializer_data
    assert "referenced_by" not in serializer_data
    assert "datasize" not in serializer_data
    assert "is_favorite" in serializer_data
    assert serializer_data["is_favorite"] == fake_email.is_favorite
    assert "eml_filepath" not in serializer_data
    assert "html_version" not in serializer_data
    assert "mailbox" not in serializer_data
    assert "headers" not in serializer_data
    assert "x_spam" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert "replies" not in serializer_data
    assert "attachments" not in serializer_data
    assert "correspondents" not in serializer_data
    assert len(serializer_data) == 1
