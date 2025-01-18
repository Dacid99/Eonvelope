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

"""Test module for :mod:`Emailkasten.Serializers.DaemonSerializers.BaseDaemonSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from Emailkasten.Serializers.DaemonSerializers.BaseDaemonSerializer import \
    BaseDaemonSerializer

from ...models.test_DaemonModel import fixture_daemonModel

@pytest.mark.django_db
def test_output(daemon):
    """Tests for the expected output of the serializer."""
    serializerData = BaseDaemonSerializer(instance=daemon).data

    assert 'id' in serializerData
    assert serializerData['id'] == daemon.id
    assert 'log_filepath' not in serializerData
    assert 'uuid' in serializerData
    assert serializerData['uuid'] == str(daemon.uuid)
    assert 'mailbox' in serializerData
    assert serializerData['mailbox'] == daemon.mailbox.id
    assert 'fetching_criterion' in serializerData
    assert serializerData['fetching_criterion'] == daemon.fetching_criterion
    assert 'cycle_interval' in serializerData
    assert serializerData['cycle_interval'] == daemon.cycle_interval
    assert 'is_running' in serializerData
    assert serializerData['is_running'] == daemon.is_running
    assert 'is_healthy' in serializerData
    assert serializerData['is_healthy'] == daemon.is_healthy
    assert 'created' in serializerData
    assert datetime.fromisoformat(serializerData['created']) == daemon.created
    assert 'updated' in serializerData
    assert datetime.fromisoformat(serializerData['updated']) == daemon.updated
    assert len(serializerData) == 9


@pytest.mark.django_db
def test_input(daemon):
    """Tests for the expected input of the serializer."""
    serializer = BaseDaemonSerializer(data=model_to_dict(daemon))
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert 'id' not in serializerData
    assert 'log_filepath' not in serializerData
    assert 'uuid' not in serializerData
    assert 'mailbox' not in serializerData
    assert 'fetching_criterion' in serializerData
    assert serializerData['fetching_criterion'] == daemon.fetching_criterion
    assert 'cycle_interval' in serializerData
    assert serializerData['cycle_interval'] == daemon.cycle_interval
    assert 'is_running' not in serializerData
    assert 'is_healthy' not in serializerData
    assert 'created' not in serializerData
    assert 'updated' not in serializerData
    assert len(serializerData) == 2
