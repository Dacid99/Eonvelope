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

from Emailkasten.Serializers.EMailSerializers.SimpleEMailSerializer import \
    SimpleEMailSerializer

from ...models.test_EMailModel import fixture_emailModel

@pytest.mark.django_db
def test_output(email):
    serializerData = SimpleEMailSerializer(instance=email).data

    assert 'id' in serializerData
    assert 'message_id' in serializerData
    assert 'datetime' in serializerData
    assert 'email_subject' in serializerData
    assert 'bodytext' in serializerData
    assert 'inReplyTo' in serializerData
    assert 'datasize' in serializerData
    assert 'is_favorite' in serializerData
    assert 'eml_filepath' not in serializerData
    assert 'prerender_filepath' not in serializerData
    assert 'account' in serializerData
    assert 'comments' in serializerData
    assert 'keywords' in serializerData
    assert 'importance' in serializerData
    assert 'priority' in serializerData
    assert 'precedence' in serializerData
    assert 'received' in serializerData
    assert 'user_agent' in serializerData
    assert 'auto_submitted' in serializerData
    assert 'content_type' in serializerData
    assert 'content_language' in serializerData
    assert 'content_location' in serializerData
    assert 'x_priority' in serializerData
    assert 'x_originated_client' in serializerData
    assert 'x_spam' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData
    assert 'attachments' not in serializerData
    assert 'images' not in serializerData
    assert 'mailinglist' in serializerData
    assert 'correspondents' in serializerData

    assert len(serializerData) == 27


@pytest.mark.django_db
def test_input(email):
    serializer = SimpleEMailSerializer(data=model_to_dict(email))
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
