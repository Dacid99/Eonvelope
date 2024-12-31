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

from Emailkasten.Serializers.MailingListSerializers.SimpleMailingListSerializer import \
    SimpleMailingListSerializer

from ...models.test_MailingListModel import fixture_mailingListModel

@pytest.mark.django_db
def test_output(mailingList):
    serializerData = SimpleMailingListSerializer(instance=mailingList).data

    assert 'id' in serializerData
    assert 'list_id' in serializerData
    assert 'list_owner' in serializerData
    assert 'list_subscribe' in serializerData
    assert 'list_unsubscribe' in serializerData
    assert 'list_post' in serializerData
    assert 'list_help' in serializerData
    assert 'list_archive' in serializerData
    assert 'is_favorite' in serializerData
    assert 'correspondent' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData
    assert 'emails' not in serializerData
    assert 'email_number' in serializerData
    assert len(serializerData) == 13


@pytest.mark.django_db
def test_input(mailingList):
    serializer = SimpleMailingListSerializer(data=model_to_dict(mailingList))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'list_id' not in serializerData
    assert 'list_owner' not in serializerData
    assert 'list_subscribe' not in serializerData
    assert 'list_unsubscribe' not in serializerData
    assert 'list_post' not in serializerData
    assert 'list_help' not in serializerData
    assert 'list_archive' not in serializerData
    assert 'is_favorite' in serializerData
    assert 'correspondent' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert 'emails' not in serializerData
    assert 'email_number' not in serializerData
    assert len(serializerData) == 1
