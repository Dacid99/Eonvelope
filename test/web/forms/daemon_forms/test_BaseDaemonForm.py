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

"""Test module for the :class:`web.forms.daemon_forms.BaseDaemonForm.BaseDaemonForm` form class."""

import pytest
from django.forms.models import model_to_dict

from web.forms.daemon_forms.BaseDaemonForm import BaseDaemonForm


@pytest.mark.django_db
def test_post_update(daemonModel):
    """Tests post direction of :class:`web.forms.daemon_forms.BaseDaemonForm.BaseDaemonForm`."""
    form = BaseDaemonForm(instance=daemonModel, data=model_to_dict(daemonModel))

    assert form.is_valid()
    form_data = form.cleaned_data
    assert "fetching_criterion" in form_data
    assert form_data["fetching_criterion"] == daemonModel.fetching_criterion
    assert "cycle_interval" in form_data
    assert form_data["cycle_interval"] == daemonModel.cycle_interval
    assert "restart_time" in form_data
    assert form_data["restart_time"] == daemonModel.restart_time
    assert "log_backup_count" in form_data
    assert form_data["log_backup_count"] == daemonModel.log_backup_count
    assert "logfile_size" in form_data
    assert form_data["logfile_size"] == daemonModel.logfile_size
    assert "mailbox" not in form_data
    assert "is_running" not in form_data
    assert "is_healthy" not in form_data
    assert "log_filepath" not in form_data
    assert "created" not in form_data
    assert "updated" not in form_data
    assert len(form_data) == 5


@pytest.mark.django_db
def test_get(daemonModel):
    """Tests get direction of :class:`web.forms.daemon_forms.BaseDaemonForm.BaseDaemonForm`."""
    form = BaseDaemonForm(instance=daemonModel)
    form_initial_data = form.initial
    form_fields = form.fields

    assert "fetching_criterion" in form_fields
    assert "fetching_criterion" in form_initial_data
    assert form_initial_data["fetching_criterion"] == daemonModel.fetching_criterion
    assert "cycle_interval" in form_fields
    assert "cycle_interval" in form_initial_data
    assert form_initial_data["cycle_interval"] == daemonModel.cycle_interval
    assert "restart_time" in form_fields
    assert "restart_time" in form_initial_data
    assert form_initial_data["restart_time"] == daemonModel.restart_time
    assert "log_backup_count" in form_fields
    assert "log_backup_count" in form_initial_data
    assert form_initial_data["log_backup_count"] == daemonModel.log_backup_count
    assert "logfile_size" in form_fields
    assert "logfile_size" in form_initial_data
    assert form_initial_data["logfile_size"] == daemonModel.logfile_size
    assert "mailbox" not in form_fields
    assert "is_running" not in form_fields
    assert "is_healthy" not in form_fields
    assert "log_filepath" not in form_fields
    assert "created" not in form_fields
    assert "updated" not in form_fields
    assert len(form_fields) == 5
