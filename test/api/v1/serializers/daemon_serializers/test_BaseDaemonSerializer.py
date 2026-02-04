# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker

from api.v1.serializers.daemon_serializers.BaseDaemonSerializer import (
    BaseDaemonSerializer,
)
from core.constants import EmailFetchingCriterionChoices, EmailProtocolChoices
from core.models import Mailbox


@pytest.mark.django_db
def test_output(fake_daemon, request_context):
    """Tests for the expected output of the serializer."""
    serializer_data = BaseDaemonSerializer(
        instance=fake_daemon, context=request_context
    ).data

    assert "id" in serializer_data
    assert serializer_data["id"] == fake_daemon.id
    assert "uuid" in serializer_data
    assert serializer_data["uuid"] == str(fake_daemon.uuid)
    assert "mailbox" in serializer_data
    assert serializer_data["mailbox"] == fake_daemon.mailbox.id
    assert "fetching_criterion" in serializer_data
    assert serializer_data["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "fetching_criterion_arg" in serializer_data
    assert (
        serializer_data["fetching_criterion_arg"] == fake_daemon.fetching_criterion_arg
    )
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
    assert "last_error" in serializer_data
    assert serializer_data["last_error"] == fake_daemon.last_error
    assert "is_healthy" in serializer_data
    assert serializer_data["is_healthy"] == fake_daemon.is_healthy
    assert "last_error" in serializer_data
    assert serializer_data["last_error"] == fake_daemon.last_error
    assert "last_error_occurred_at" in serializer_data
    assert (
        serializer_data["last_error_occurred_at"] == fake_daemon.last_error_occurred_at
    )
    assert "created" in serializer_data
    assert datetime.fromisoformat(serializer_data["created"]) == fake_daemon.created
    assert "updated" in serializer_data
    assert datetime.fromisoformat(serializer_data["updated"]) == fake_daemon.updated
    assert len(serializer_data) == 12


@pytest.mark.django_db
def test_input(daemon_with_interval_payload, request_context):
    """Tests for the expected input of the serializer."""
    serializer = BaseDaemonSerializer(
        data=daemon_with_interval_payload, context=request_context
    )
    assert serializer.is_valid()
    serializer_data = serializer.validated_data

    assert "id" not in serializer_data
    assert "uuid" not in serializer_data
    assert "mailbox" in serializer_data
    assert isinstance(serializer_data["mailbox"], Mailbox)
    assert serializer_data["mailbox"].id == daemon_with_interval_payload["mailbox"]
    assert "fetching_criterion" in serializer_data
    assert (
        serializer_data["fetching_criterion"]
        == daemon_with_interval_payload["fetching_criterion"]
    )
    assert "fetching_criterion_arg" in serializer_data
    assert (
        serializer_data["fetching_criterion_arg"]
        == daemon_with_interval_payload["fetching_criterion_arg"]
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
    assert "last_error" not in serializer_data
    assert "is_healthy" not in serializer_data
    assert "last_error" not in serializer_data
    assert "last_error_occurred_at" not in serializer_data
    assert "created" not in serializer_data
    assert "updated" not in serializer_data
    assert len(serializer_data) == 4


@pytest.mark.django_db
def test_post__other_mailbox(
    fake_daemon,
    daemon_with_interval_payload,
    fake_other_mailbox,
    request_context,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["mailbox"] = fake_other_mailbox.id

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["mailbox"].errors


@pytest.mark.django_db
def test_post__unknown_mailbox(
    fake_daemon,
    daemon_with_interval_payload,
    request_context,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["mailbox"] = 1000

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["mailbox"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_fetching_criterion", ["OTHER"])
def test_post__bad_fetching_criterion(
    fake_daemon, daemon_with_interval_payload, request_context, bad_fetching_criterion
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["fetching_criterion"] = bad_fetching_criterion

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["fetching_criterion"].errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "unavailable_fetching_criterion",
    [
        EmailFetchingCriterionChoices.ANNUALLY,
        EmailFetchingCriterionChoices.DRAFT,
        EmailFetchingCriterionChoices.UNANSWERED,
    ],
)
def test_post__unavailable_fetching_criterion(
    fake_daemon,
    daemon_with_interval_payload,
    request_context,
    unavailable_fetching_criterion,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    fake_daemon.mailbox.account.protocol = EmailProtocolChoices.POP3
    fake_daemon.mailbox.account.save(update_fields=["protocol"])
    fake_daemon.refresh_from_db()
    daemon_with_interval_payload["fetching_criterion"] = unavailable_fetching_criterion

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["fetching_criterion"].errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("int_arg_fetching_criterion", "bad_int_arg"),
    [
        (EmailFetchingCriterionChoices.LARGER, "no int"),
        (EmailFetchingCriterionChoices.SMALLER, "-11"),
    ],
)
def test_post__bad_int_fetching_criterion_arg(
    fake_daemon,
    daemon_with_interval_payload,
    request_context,
    int_arg_fetching_criterion,
    bad_int_arg,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["fetching_criterion"] = int_arg_fetching_criterion
    daemon_with_interval_payload["fetching_criterion_arg"] = bad_int_arg

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["fetching_criterion_arg"].errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "date_arg_fetching_criterion",
    [
        EmailFetchingCriterionChoices.SENTSINCE,
    ],
)
def test_post__bad_date_fetching_criterion_arg(
    fake_daemon,
    daemon_with_interval_payload,
    request_context,
    date_arg_fetching_criterion,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["fetching_criterion"] = date_arg_fetching_criterion
    daemon_with_interval_payload["fetching_criterion_arg"] = "no time"

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["fetching_criterion_arg"].errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "arg_fetching_criterion",
    [
        EmailFetchingCriterionChoices.BODY,
        EmailFetchingCriterionChoices.SUBJECT,
    ],
)
def test_post__missing_fetching_criterion_arg(
    fake_daemon,
    daemon_with_interval_payload,
    request_context,
    arg_fetching_criterion,
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["fetching_criterion"] = arg_fetching_criterion
    daemon_with_interval_payload["fetching_criterion_arg"] = ""

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["fetching_criterion_arg"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_period", ["other"])
def test_post__bad_interval_period(
    fake_daemon, daemon_with_interval_payload, request_context, bad_interval_period
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["interval"]["period"] = bad_interval_period

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["interval"]["period"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_every", [0, -1])
def test_post__bad_interval_every(
    fake_daemon, daemon_with_interval_payload, request_context, bad_interval_every
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer`."""
    daemon_with_interval_payload["interval"]["every"] = bad_interval_every

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )

    assert not serializer.is_valid()
    assert serializer["interval"]["every"].errors


@pytest.mark.django_db
def test_update__new_interval(
    fake_daemon, daemon_with_interval_payload, request_context
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer` with new interval data."""
    assert IntervalSchedule.objects.count() == 1

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )
    serializer.is_valid()
    serializer.save()

    assert IntervalSchedule.objects.count() == 2
    assert (
        fake_daemon.interval.every == daemon_with_interval_payload["interval"]["every"]
    )
    assert (
        fake_daemon.interval.period
        == daemon_with_interval_payload["interval"]["period"]
    )


@pytest.mark.django_db
def test_update__existing_interval(
    fake_daemon, daemon_with_interval_payload, request_context
):
    """Tests post direction of :class:`api.v1.serializers.BaseDaemonSerializer` with interval data matching an existing db entry."""
    baker.make(
        IntervalSchedule,
        every=daemon_with_interval_payload["interval"]["every"],
        period=daemon_with_interval_payload["interval"]["period"],
    )

    assert IntervalSchedule.objects.count() == 2

    serializer = BaseDaemonSerializer(
        instance=fake_daemon, data=daemon_with_interval_payload, context=request_context
    )
    serializer.is_valid()
    serializer.save()

    assert IntervalSchedule.objects.count() == 2
    assert (
        fake_daemon.interval.every == daemon_with_interval_payload["interval"]["every"]
    )
    assert (
        fake_daemon.interval.period
        == daemon_with_interval_payload["interval"]["period"]
    )


@pytest.mark.django_db
def test_input__duplicate(fake_daemon, request_context):
    """Tests input direction of :class:`api.v1.serializers.BaseAccountSerializer`."""
    payload = model_to_dict(fake_daemon)
    payload.pop("id")
    daemon_payload = {key: value for key, value in payload.items() if value is not None}
    daemon_payload["interval"] = {
        "every": abs(fake_daemon.interval.every),
        "period": fake_daemon.interval.period,
    }

    serializer = BaseDaemonSerializer(data=daemon_payload, context=request_context)

    assert not serializer.is_valid()
    assert serializer.errors
