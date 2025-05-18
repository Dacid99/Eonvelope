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

"""Test module for :mod:`api.v1.serializers.BaseDaemonSerializer`."""

from datetime import datetime

import pytest
from django.forms.models import model_to_dict

from api.v1.serializers.daemon_serializers.BaseDaemonSerializer import (
    BaseDaemonSerializer,
)


@pytest.mark.django_db
def test_output(fake_daemon, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = BaseDaemonSerializer(
        instance=fake_daemon, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_daemon.id
    assert "log_filepath" not in serializer_data
    assert "uuid" in serializer_data
    assert serializer_data["uuid"] == str(fake_daemon.uuid)
    assert "mailbox" in serializer_data
    assert serializer_data["mailbox"] == fake_daemon.mailbox.id
    assert "fetching_criterion" in serializer_data
    assert serializer_data["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "cycle_interval" in serializer_data
    assert serializer_data["cycle_interval"] == fake_daemon.cycle_interval
    assert "restart_time" in serializer_data
    assert serializer_data["restart_time"] == fake_daemon.restart_time
    assert "log_backup_count" in serializer_data
    assert serializer_data["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in serializer_data
    assert serializer_data["logfile_size"] == fake_daemon.logfile_size
    assert "is_running" in serializer_data
    assert serializer_data["is_running"] == fake_daemon.is_running
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_daemon.is_healthy
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_daemon.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_daemon.updated
    assert len(serializer_data) == 12


@pytest.mark.django_db
def test_input(fake_daemon, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseDaemonSerializer(
        data=model_to_dict(fake_daemon), context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "log_filepath" not in serializer_data
    assert "uuid" not in serializer_data
    assert "mailbox" not in serializer_data
    assert "fetching_criterion" in serializer_data
    assert serializer_data["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "cycle_interval" in serializer_data
    assert serializer_data["cycle_interval"] == fake_daemon.cycle_interval
    assert "restart_time" in serializer_data
    assert serializer_data["restart_time"] == fake_daemon.restart_time
    assert "log_backup_count" in serializer_data
    assert serializer_data["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in serializer_data
    assert serializer_data["logfile_size"] == fake_daemon.logfile_size
    assert "is_running" not in serializer_data
    assert "is_healthy" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 5


@pytest.mark.django_db
def test_validation_failure(fake_daemon):
    """Tests validation of :attr:`core.models.Daemon.Daemon.fetching_criterion`."""
    fake_daemon.fetching_criterion = "OTHER"
    serializer = BaseDaemonSerializer(data=model_to_dict(fake_daemon))
    assert not serializer.is_valid()
