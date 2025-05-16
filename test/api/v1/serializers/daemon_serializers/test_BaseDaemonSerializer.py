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

"""Test module for :mod:`api.v1.serializers.DaemonSerializers.BaseDaemonSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.daemon_serializers.BaseDaemonSerializer import (
    BaseDaemonSerializer,
)


@pytest.mark.django_db
def test_output(fake_daemon, request_context):
    """Tests for the expected output of the serializer."""
    serializerData = BaseDaemonSerializer(
        instance=fake_daemon, context=request_context
    ).data

    assert "id" in serializerData
    assert serializerData["id"] == fake_daemon.id
    assert "log_filepath" not in serializerData
    assert "uuid" in serializerData
    assert serializerData["uuid"] == str(fake_daemon.uuid)
    assert "mailbox" in serializerData
    assert serializerData["mailbox"] == fake_daemon.mailbox.id
    assert "fetching_criterion" in serializerData
    assert serializerData["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "cycle_interval" in serializerData
    assert serializerData["cycle_interval"] == fake_daemon.cycle_interval
    assert "restart_time" in serializerData
    assert serializerData["restart_time"] == fake_daemon.restart_time
    assert "log_backup_count" in serializerData
    assert serializerData["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in serializerData
    assert serializerData["logfile_size"] == fake_daemon.logfile_size
    assert "is_running" in serializerData
    assert serializerData["is_running"] == fake_daemon.is_running
    assert "is_healthy" in serializerData
    assert serializerData["is_healthy"] == fake_daemon.is_healthy
    assert "created" in serializerData
    assert datetime.fromisoformat(serializerData["created"]) == fake_daemon.created
    assert "updated" in serializerData
    assert datetime.fromisoformat(serializerData["updated"]) == fake_daemon.updated
    assert len(serializerData) == 12


@pytest.mark.django_db
def test_input(fake_daemon, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseDaemonSerializer(
        data=model_to_dict(fake_daemon), context=request_context
    )
    assert serializer.is_valid()
    serializerData = serializer.validated_data

    assert "id" not in serializerData
    assert "log_filepath" not in serializerData
    assert "uuid" not in serializerData
    assert "mailbox" not in serializerData
    assert "fetching_criterion" in serializerData
    assert serializerData["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "cycle_interval" in serializerData
    assert serializerData["cycle_interval"] == fake_daemon.cycle_interval
    assert "restart_time" in serializerData
    assert serializerData["restart_time"] == fake_daemon.restart_time
    assert "log_backup_count" in serializerData
    assert serializerData["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in serializerData
    assert serializerData["logfile_size"] == fake_daemon.logfile_size
    assert "is_running" not in serializerData
    assert "is_healthy" not in serializerData
    assert "created" not in serializerData
    assert "updated" not in serializerData
    assert len(serializerData) == 5


@pytest.mark.django_db
def test_validation_failure(fake_daemon):
    """Tests validation of :attr:`core.models.Daemon.Daemon.fetching_criterion`."""
    fake_daemon.fetching_criterion = "OTHER"
    serializer = BaseDaemonSerializer(data=model_to_dict(fake_daemon))
    assert not serializer.is_valid()
