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

"""Test module for the :class:`web.forms.BaseDaemonForm` form class."""

import pytest
from django_celery_beat.models import IntervalSchedule
from model_bakery import baker

from web.forms import BaseDaemonForm


@pytest.mark.django_db
def test_post_update(fake_daemon, daemon_with_interval_payload):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    form = BaseDaemonForm(instance=fake_daemon, data=daemon_with_interval_payload)

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "fetching_criterion" in form_data
    assert (
        form_data["fetching_criterion"]
        == daemon_with_interval_payload["fetching_criterion"]
    )
    assert "interval_every" in form_data
    assert form_data["interval_every"] == daemon_with_interval_payload["interval_every"]
    assert "interval_period" in form_data
    assert (
        form_data["interval_period"] == daemon_with_interval_payload["interval_period"]
    )
    assert "celery_task" not in form_data
    assert "log_backup_count" in form_data
    assert (
        form_data["log_backup_count"]
        == daemon_with_interval_payload["log_backup_count"]
    )
    assert "logfile_size" in form_data
    assert form_data["logfile_size"] == daemon_with_interval_payload["logfile_size"]
    assert "mailbox" not in form_data
    assert "is_healthy" not in form_data
    assert "log_filepath" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 5


@pytest.mark.django_db
@pytest.mark.parametrize("bad_fetching_criterion", ["OTHER"])
def test_post_bad_fetching_criterion(
    fake_daemon, daemon_payload, bad_fetching_criterion
):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    daemon_payload["fetching_criterion"] = bad_fetching_criterion

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_payload)

    assert not form.is_valid()
    assert form["fetching_criterion"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_period", ["other"])
def test_post_bad_interval_period(fake_daemon, daemon_payload, bad_interval_period):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    daemon_payload["interval_period"] = bad_interval_period

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_payload)

    assert not form.is_valid()
    assert form["interval_period"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_interval_every", [0, -1])
def test_post_bad_interval_every(fake_daemon, daemon_payload, bad_interval_every):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    daemon_payload["interval_every"] = bad_interval_every

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_payload)

    assert not form.is_valid()
    assert form["interval_every"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_log_backup_count", [-1])
def test_post_bad_log_backup_count(fake_daemon, daemon_payload, bad_log_backup_count):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    daemon_payload["log_backup_count"] = bad_log_backup_count

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_payload)

    assert not form.is_valid()
    assert form["log_backup_count"].errors


@pytest.mark.django_db
@pytest.mark.parametrize("bad_logfile_size", [-1])
def test_post_bad_logfile_size(fake_daemon, daemon_payload, bad_logfile_size):
    """Tests post direction of :class:`web.forms.BaseDaemonForm`."""
    daemon_payload["logfile_size"] = bad_logfile_size

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_payload)

    assert not form.is_valid()
    assert form["logfile_size"].errors


@pytest.mark.django_db
def test_get(fake_daemon):
    """Tests get direction of :class:`web.forms.BaseDaemonForm`."""
    form = BaseDaemonForm(instance=fake_daemon)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "fetching_criterion" in form_fields
    assert "fetching_criterion" in form_initial_data
    assert form_initial_data["fetching_criterion"] == fake_daemon.fetching_criterion
    assert "interval_every" in form_fields
    assert "interval_every" in form_initial_data
    assert form_initial_data["interval_every"] == fake_daemon.interval.every
    assert "interval_period" in form_fields
    assert "interval_period" in form_initial_data
    assert form_initial_data["interval_period"] == fake_daemon.interval.period
    assert "celery_task" not in form_fields
    assert "log_backup_count" in form_fields
    assert "log_backup_count" in form_initial_data
    assert form_initial_data["log_backup_count"] == fake_daemon.log_backup_count
    assert "logfile_size" in form_fields
    assert "logfile_size" in form_initial_data
    assert form_initial_data["logfile_size"] == fake_daemon.logfile_size
    assert "mailbox" not in form_fields
    assert "is_healthy" not in form_fields
    assert "log_filepath" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 5


@pytest.mark.django_db
def test_save_new_interval(fake_daemon, daemon_with_interval_payload):
    assert IntervalSchedule.objects.count() == 1

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_with_interval_payload)
    form.is_valid()
    form.save()

    assert IntervalSchedule.objects.count() == 2
    assert fake_daemon.interval.every == daemon_with_interval_payload["interval_every"]
    assert (
        fake_daemon.interval.period == daemon_with_interval_payload["interval_period"]
    )


@pytest.mark.django_db
def test_save_existing_interval(fake_daemon, daemon_with_interval_payload):
    baker.make(
        IntervalSchedule,
        every=daemon_with_interval_payload["interval_every"],
        period=daemon_with_interval_payload["interval_period"],
    )

    assert IntervalSchedule.objects.count() == 2

    form = BaseDaemonForm(instance=fake_daemon, data=daemon_with_interval_payload)
    form.is_valid()
    form.save()

    assert IntervalSchedule.objects.count() == 2
    assert fake_daemon.interval.every == daemon_with_interval_payload["interval_every"]
    assert (
        fake_daemon.interval.period == daemon_with_interval_payload["interval_period"]
    )
