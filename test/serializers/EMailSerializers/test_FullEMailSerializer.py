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

"""Test module for :mod:`api.v1.serializers.EMailSerializers.FullEMailSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.email_serializers.FullEMailSerializer import \
    FullEMailSerializer

from ...models.test_EMailModel import fixture_emailModel

@pytest.mark.django_db
def test_output(email):
    """Tests for the expected output of the serializer."""
    serializerData = FullEMailSerializer(instance=email).data

    assert 'id' in serializerData
    assert serializerData['id'] == email.id
    assert 'message_id' in serializerData
    assert serializerData['message_id'] == email.message_id
    assert 'datetime' in serializerData
    assert datetime.fromisoformat(serializerData['datetime']) == email.datetime
    assert 'email_subject' in serializerData
    assert serializerData['email_subject'] == email.email_subject
    assert 'bodytext' in serializerData
    assert serializerData['bodytext'] == email.bodytext
    assert 'inReplyTo' in serializerData
    assert serializerData['inReplyTo'] is None
    assert 'datasize' in serializerData
    assert serializerData['datasize'] == email.datasize
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == email.is_favorite
    assert 'eml_filepath' not in serializerData
    assert 'prerender_filepath' not in serializerData
    assert 'account' in serializerData
    assert serializerData['account'] == email.account.id
    assert 'comments' in serializerData
    assert serializerData['comments'] == email.comments
    assert 'keywords' in serializerData
    assert serializerData['keywords'] == email.keywords
    assert 'importance' in serializerData
    assert serializerData['importance'] == email.importance
    assert 'priority' in serializerData
    assert serializerData['priority'] == email.priority
    assert 'precedence' in serializerData
    assert serializerData['precedence'] == email.precedence
    assert 'received' in serializerData
    assert serializerData['received'] == email.received
    assert 'user_agent' in serializerData
    assert serializerData['user_agent'] == email.user_agent
    assert 'auto_submitted' in serializerData
    assert serializerData['auto_submitted'] == email.auto_submitted
    assert 'content_type' in serializerData
    assert serializerData['content_type'] == email.content_type
    assert 'content_language' in serializerData
    assert serializerData['content_language'] == email.content_language
    assert 'content_location' in serializerData
    assert serializerData['content_location'] == email.content_location
    assert 'x_priority' in serializerData
    assert serializerData['x_priority'] == email.x_priority
    assert 'x_originated_client' in serializerData
    assert serializerData['x_originated_client'] == email.x_originated_client
    assert 'x_spam' in serializerData
    assert serializerData['x_spam'] == email.x_spam
    assert 'created' in serializerData
    assert datetime.fromisoformat(serializerData['created']) == email.created
    assert 'updated' in serializerData
    assert datetime.fromisoformat(serializerData['updated']) == email.updated
    assert 'attachments' in serializerData
    assert serializerData['attachments'] == []
    assert 'images' in serializerData
    assert serializerData['images'] == []
    assert 'mailinglist' in serializerData
    assert serializerData['mailinglist'] is None
    assert 'correspondents' in serializerData
    assert serializerData['correspondents'] == []

    assert len(serializerData) == 29


@pytest.mark.django_db
def test_input(email):
    """Tests for the expected input of the serializer."""
    serializer = FullEMailSerializer(data=model_to_dict(email))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'message_id' not in serializerData
    assert 'datetime' not in serializerData
    assert 'email_subject' not in serializerData
    assert 'bodytext' not in serializerData
    assert 'inReplyTo' not in serializerData
    assert 'datasize' not in serializerData
    assert 'is_favorite' in serializerData
    assert serializerData['is_favorite'] == email.is_favorite
    assert 'eml_filepath' not in serializerData
    assert 'prerender_filepath' not in serializerData
    assert 'account' not in serializerData
    assert 'comments' not in serializerData
    assert 'keywords' not in serializerData
    assert 'importance' not in serializerData
    assert 'priority' not in serializerData
    assert 'precedence' not in serializerData
    assert 'received' not in serializerData
    assert 'user_agent' not in serializerData
    assert 'auto_submitted' not in serializerData
    assert 'content_type' not in serializerData
    assert 'content_language' not in serializerData
    assert 'content_location' not in serializerData
    assert 'x_priority' not in serializerData
    assert 'x_originated_client' not in serializerData
    assert 'x_spam' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert 'attachments' not in serializerData
    assert 'images' not in serializerData
    assert 'mailinglist' not in serializerData
    assert 'correspondents' not in serializerData

    assert len(serializerData) == 1
