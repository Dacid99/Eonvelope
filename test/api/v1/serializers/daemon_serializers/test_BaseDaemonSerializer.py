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
    assert "interval" in serializer_data
    assert isinstance(serializer_data["interval"], dict)
    assert "every" in serializer_data["interval"]
    assert serializer_data["interval"]["every"] == fake_daemon.interval.every
    assert "period" in serializer_data["interval"]
    assert serializer_data["interval"]["period"] == fake_daemon.interval.period
    assert "celery_task" in serializer_data
    assert isinstance(serializer_data["celery_task"], dict)
    assert "enabled" in serializer_data["celery_task"]
    assert serializer_data["celery_task"]["enabled"] == fake_daemon.celery_task.enabled
    assert "last_run_at" in serializer_data["celery_task"]
    assert (
        serializer_data["celery_task"]["last_run_at"]
        == fake_daemon.celery_task.last_run_at
    )
    assert "total_run_count" in serializer_data["celery_task"]
    assert (
        serializer_data["celery_task"]["total_run_count"]
        == fake_daemon.celery_task.total_run_count
    )
    assert "log_backup_count" in serializer_data
    assert serializer_data["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in serializer_data
    assert serializer_data["logfile_size"] == fake_daemon.logfile_size
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_daemon.is_healthy
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_daemon.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_daemon.updated
    assert len(serializer_data) == 11


@pytest.mark.django_db
def test_input(daemon_with_interval_payload, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseDaemonSerializer(
        data=daemon_with_interval_payload, context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "log_filepath" not in serializer_data
    assert "uuid" not in serializer_data
    assert "mailbox" not in serializer_data
    assert "fetching_criterion" in serializer_data
    assert (
        serializer_data["fetching_criterion"]
        == daemon_with_interval_payload["fetching_criterion"]
    )
    assert "interval" in serializer_data
    assert isinstance(serializer_data["interval"], dict)
    assert "every" in serializer_data["interval"]
    assert (
        serializer_data["interval"]["every"]
        == daemon_with_interval_payload["interval"]["every"]
    )
    assert "period" in serializer_data["interval"]
    assert (
        serializer_data["interval"]["period"]
        == daemon_with_interval_payload["interval"]["period"]
    )
    assert "celery_task" not in serializer_data
    assert "log_backup_count" in serializer_data
    assert (
        serializer_data["log_backup_count"]
        == daemon_with_interval_payload["log_backup_count"]
    )
    assert "logfile_size" in serializer_data
    assert (
        serializer_data["logfile_size"] == daemon_with_interval_payload["logfile_size"]
    )
    assert "is_healthy" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 4


@pytest.mark.django_db
@pytest.mark.parametrize("bad_fetching_criterion", ["OTHER"])
def test_post_bad_fetching_criterion(
    fake_daemon, daemon_payload, bad_fetching_criterion
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_payload["fetching_criterion"] = bad_fetching_criterion

    serializer = BaseDaemonSerializer(instance=fake_daemon, data=daemon_payload)

    assert not serializer.is_valid()
    assert serializer["fetching_criterion"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_period", ["other"])
def test_post_bad_interval_period(
    fake_daemon, daemon_with_interval_payload, bad_interval_period
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["interval"]["period"] = bad_interval_period

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload
    )

    assert not serializer.is_valid()
    assert serializer["interval"]["period"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_every", [0, -1])
def test_post_bad_interval_every(
    fake_daemon, daemon_with_interval_payload, bad_interval_every
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["interval"]["every"] = bad_interval_every

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload
    )

    assert not serializer.is_valid()
    assert serializer["interval"]["every"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_log_backup_count", [-1])
def test_post_bad_log_backup_count(fake_daemon, daemon_payload, bad_log_backup_count):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_payload["log_backup_count"] = bad_log_backup_count

    serializer = BaseDaemonSerializer(instance=fake_daemon, data=daemon_payload)

    assert not serializer.is_valid()
    assert serializer["log_backup_count"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_logfile_size", [-1])
def test_post_bad_logfile_size(fake_daemon, daemon_payload, bad_logfile_size):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_payload["logfile_size"] = bad_logfile_size

    serializer = BaseDaemonSerializer(instance=fake_daemon, data=daemon_payload)

    assert not serializer.is_valid()
    assert serializer["logfile_size"].errors


@pytest.mark.django_db
def test_validation_failure(fake_daemon):
    """Tests validation of :attr:`core.models.Daemon.Daemon.fetching_criterion`."""
    fake_daemon.fetching_criterion = "OTHER"
    serializer = BaseDaemonSerializer(data=model_to_dict(fake_daemon))
    assert not serializer.is_valid()
