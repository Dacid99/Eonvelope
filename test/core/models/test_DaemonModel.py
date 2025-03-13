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

"""Test module for :mod:`core.models.DaemonModel`.

Fixtures:
    :func:`fixture_daemonModelModel`: Creates an :class:`core.models.DaemonModel.DaemonModel` instance for testing.
"""

import datetime
import os
from uuid import UUID

import pytest
from django.db import IntegrityError
from model_bakery import baker

import Emailkasten.constants
from core import constants
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel
from Emailkasten.utils import get_config


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks the :attr:`core.models.DaemonModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.DaemonModel.logger", autospec=True)


@pytest.mark.django_db
def test_DaemonModel_default_creation(daemonModel):
    """Tests the correct default creation of :class:`core.models.DaemonModel.DaemonModel`."""
    assert daemonModel.uuid is not None
    assert isinstance(daemonModel.uuid, UUID)
    assert daemonModel.mailbox is not None
    assert isinstance(daemonModel.mailbox, MailboxModel)
    assert daemonModel.fetching_criterion == constants.EmailFetchingCriterionChoices.ALL
    assert daemonModel.cycle_interval == get_config("DAEMON_CYCLE_PERIOD_DEFAULT")
    assert daemonModel.restart_time == get_config("DAEMON_RESTART_TIME_DEFAULT")
    assert daemonModel.is_running is False
    assert daemonModel.is_healthy is True
    assert daemonModel.log_filepath is not None
    assert daemonModel.log_backup_count == get_config("DAEMON_LOG_BACKUP_COUNT_DEFAULT")
    assert daemonModel.logfile_size == get_config("DAEMON_LOGFILE_SIZE_DEFAULT")
    assert daemonModel.updated is not None
    assert isinstance(daemonModel.updated, datetime.datetime)
    assert daemonModel.created is not None
    assert isinstance(daemonModel.created, datetime.datetime)


@pytest.mark.django_db
def test_DaemonModel___str__(daemonModel):
    assert str(daemonModel.uuid) in str(daemonModel)
    assert str(daemonModel.mailbox) in str(daemonModel)


@pytest.mark.django_db
def test_MailboxModel_foreign_key_deletion(daemonModel):
    """Tests the on_delete foreign key constraint in :class:`core.models.AccountModel.AccountModel`."""
    assert daemonModel is not None

    daemonModel.mailbox.delete()

    with pytest.raises(DaemonModel.DoesNotExist):
        daemonModel.refresh_from_db()


@pytest.mark.django_db
def test_DaemonModel_unique(daemonModel):
    """Tests the unique constraints of :class:`core.models.DaemonModel.DaemonModel`."""
    with pytest.raises(IntegrityError):
        baker.make(DaemonModel, log_filepath=daemonModel.log_filepath)


@pytest.mark.django_db
def test_DaemonModel_save_logfileCreation(daemonModel):
    daemonModel.log_filepath = None

    daemonModel.save()

    daemonModel.refresh_from_db()
    assert daemonModel.log_filepath == os.path.join(
        Emailkasten.constants.LoggerConfiguration.LOG_DIRECTORY_PATH,
        f"daemon_{daemonModel.uuid}.log",
    )
