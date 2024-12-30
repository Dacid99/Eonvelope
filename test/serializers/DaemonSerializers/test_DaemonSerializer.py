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

from Emailkasten.Serializers.DaemonSerializers.DaemonSerializer import \
    DaemonSerializer

from ...models.test_DaemonModel import fixture_daemonModel

@pytest.mark.django_db
def test_output(daemon):
    serializerData = DaemonSerializer(instance=daemon).data

    assert 'log_filepath' not in serializerData
    assert 'uuid' in serializerData
    assert 'mailbox' in serializerData
    assert 'fetching_criterion' in serializerData
    assert 'cycle_interval' in serializerData
    assert 'is_running' in serializerData
    assert 'is_healthy' in serializerData
    assert 'created' in serializerData
    assert 'updated' in serializerData


@pytest.mark.django_db
def test_input(daemon):
    serializer = DaemonSerializer(data=model_to_dict(daemon))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'log_filepath' not in serializerData
    assert 'uuid' not in serializerData
    assert 'mailbox' not in serializerData
    assert 'fetching_criterion' in serializerData
    assert 'cycle_interval' in serializerData
    assert 'is_running' not in serializerData
    assert 'is_healthy' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
