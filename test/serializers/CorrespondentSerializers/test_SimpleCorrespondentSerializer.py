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

from Emailkasten.Serializers.CorrespondentSerializers.SimpleCorrespondentSerializer import \
    SimpleCorrespondentSerializer

from ...models.test_CorrespondentModel import fixture_correspondentModel

@pytest.mark.django_db
def test_output(correspondent):
    serializerData = SimpleCorrespondentSerializer(instance=correspondent).data

    assert 'id' in serializerData
    assert 'emails' not in serializerData
    assert 'mailinglist' not in serializerData
    assert 'email_name' in serializerData
    assert 'email_address' in serializerData
    assert 'is_favorite' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData
    assert len(serializerData) == 6


@pytest.mark.django_db
def test_input(correspondent):
    serializer = SimpleCorrespondentSerializer(data=model_to_dict(correspondent))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'emails' not in serializerData
    assert 'mailinglist' not in serializerData
    assert 'email_name' in serializerData
    assert 'email_address' not in serializerData
    assert 'is_favorite' in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert len(serializerData) == 2
