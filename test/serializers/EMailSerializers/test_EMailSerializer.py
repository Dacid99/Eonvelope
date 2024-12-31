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

from Emailkasten.Serializers.EMailSerializers.EMailSerializer import \
    EMailSerializer

from ...models.test_EMailModel import fixture_emailModel

@pytest.mark.django_db
def test_output(email):
    serializerData = EMailSerializer(instance=email).data

    assert 'id' in serializerData
    assert 'message_id' in serializerData
    assert 'datetime' in serializerData
    assert 'email_subject' in serializerData
    assert 'bodytext' in serializerData
    assert 'inReplyTo' in serializerData
    assert 'datasize' in serializerData
    assert 'is_favorite' in serializerData
    assert 'account' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData
    assert 'attachments' in serializerData
    assert 'images' in serializerData
    assert 'mailinglist' in serializerData
    assert 'correspondents' in serializerData
    assert len(serializerData) == 15


@pytest.mark.django_db
def test_input(email):
    serializer = EMailSerializer(data=model_to_dict(email))
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
    assert 'account' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert 'attachments' not in serializerData
    assert 'images' not in serializerData
    assert 'mailinglist' not in serializerData
    assert 'correspondents' not in serializerData
    assert len(serializerData) == 1
