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
    :func:`fixture_daemonModel`: Creates an :class:`core.models.DaemonModel.DaemonModel` instance for testing.
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


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks the :attr:`core.models.DaemonModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.DaemonModel.logger", autospec=True)


@pytest.fixture(name="daemon")
def fixture_daemonModel(faker) -> DaemonModel:
    """Creates an :class:`core.models.DaemonModel.DaemonModel`.

    Returns:
        The daemon instance for testing.
    """
    return baker.make(DaemonModel, log_filepath=faker.file_path(extension="log"))


@pytest.mark.django_db
def test_DaemonModel_default_creation(daemon):
    """Tests the correct default creation of :class:`core.models.DaemonModel.DaemonModel`."""

    assert daemon.uuid is not None
    assert isinstance(daemon.uuid, UUID)
    assert daemon.mailbox is not None
    assert isinstance(daemon.mailbox, MailboxModel)
    assert daemon.fetching_criterion == constants.EmailFetchingCriterionChoices.ALL
    assert daemon.cycle_interval == get_config("DAEMON_CYCLE_PERIOD_DEFAULT")
    assert daemon.restart_time == get_config("DAEMON_RESTART_TIME_DEFAULT")
    assert daemon.is_running is False
    assert daemon.is_healthy is True
    assert daemon.log_filepath is not None
    assert daemon.log_backup_count == get_config("DAEMON_LOG_BACKUP_COUNT_DEFAULT")
    assert daemon.logfile_size == get_config("DAEMON_LOGFILE_SIZE_DEFAULT")

    assert daemon.updated is not None
    assert isinstance(daemon.updated, datetime.datetime)
    assert daemon.created is not None
    assert isinstance(daemon.created, datetime.datetime)

    assert str(daemon.uuid) in str(daemon)
    assert str(daemon.mailbox) in str(daemon)


@pytest.mark.django_db
def test_MailboxModel_foreign_key_deletion(daemon):
    """Tests the on_delete foreign key constraint in :class:`core.models.AccountModel.AccountModel`."""

    assert daemon is not None
    daemon.mailbox.delete()
    with pytest.raises(DaemonModel.DoesNotExist):
        daemon.refresh_from_db()


@pytest.mark.django_db
def test_DaemonModel_unique(daemon):
    """Tests the unique constraints of :class:`core.models.DaemonModel.DaemonModel`."""

    with pytest.raises(IntegrityError):
        baker.make(DaemonModel, log_filepath=daemon.log_filepath)


@pytest.mark.django_db
def test_DaemonModel_save_logfileCreation(daemon):
    daemon.log_filepath = None

    daemon.save()

    daemon.refresh_from_db()
    assert daemon.log_filepath == os.path.join(
        Emailkasten.constants.LoggerConfiguration.LOG_DIRECTORY_PATH,
        f"daemon_{daemon.uuid}.log",
    )
