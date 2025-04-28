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

"""Test for :mod:`core.EMailArchiverDaemon`."""

import logging
import time

import pytest
from django.db.models.signals import post_save

from core.EMailArchiverDaemon import EMailArchiverDaemon
from core.models.DaemonModel import DaemonModel
from core.signals.save_DaemonModel import post_save_daemon


@pytest.fixture(autouse=True)
def mock_logging_FileHandler(mocker):
    return mocker.patch(
        "core.EMailArchiverDaemon.logging.handlers.RotatingFileHandler", autospec=True
    )


@pytest.fixture
def mock_logger(mocker):
    return mocker.MagicMock(spec=logging.Logger)


@pytest.fixture(autouse=True)
def mock_logging_getLogger(mocker, mock_logger):
    return mocker.patch(
        "core.EMailArchiverDaemon.logging.getLogger",
        autospec=True,
        return_value=mock_logger,
    )


@pytest.fixture
def emailArchiverDaemon(daemonModel):
    return EMailArchiverDaemon(daemonModel=daemonModel)


@pytest.mark.django_db
def test___init__(mock_logging_getLogger, daemonModel):
    emailArchiverDaemon = EMailArchiverDaemon(daemonModel)

    assert emailArchiverDaemon is not None
    assert emailArchiverDaemon.daemon
    assert str(daemonModel.uuid) in emailArchiverDaemon.name
    assert emailArchiverDaemon._daemonModel == daemonModel
    assert emailArchiverDaemon._stopEvent is not None
    assert not emailArchiverDaemon._stopEvent.is_set()
    mock_logging_getLogger.assert_called_with(str(emailArchiverDaemon))


@pytest.mark.django_db
def test_setupLogger(
    mock_logging_getLogger, mock_logger, mock_logging_FileHandler, daemonModel
):
    emailArchiverDaemon = EMailArchiverDaemon(daemonModel=daemonModel)

    mock_logging_getLogger.assert_called_with(str(emailArchiverDaemon))
    mock_logging_FileHandler.assert_called_with(
        filename=daemonModel.log_filepath,
        backupCount=daemonModel.log_backup_count,
        maxBytes=daemonModel.logfile_size,
    )
    mock_logger.addHandler.assert_called_with(mock_logging_FileHandler.return_value)


@pytest.mark.django_db
def test_start_dryrun_success(mocker, daemonModel, emailArchiverDaemon):
    mock_thread_start = mocker.patch(
        "core.EMailArchiverDaemon.threading.Thread.start", autospec=True
    )
    daemonModel.is_running = False
    daemonModel.save(update_fields=["is_running"])

    emailArchiverDaemon.start()

    daemonModel.refresh_from_db()
    assert daemonModel.is_running is True
    mock_thread_start.assert_called_once_with(emailArchiverDaemon)
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_start_dryrun_failure(mocker, daemonModel, emailArchiverDaemon):
    mock_thread_start = mocker.patch(
        "core.EMailArchiverDaemon.threading.Thread.start",
        autospec=True,
        side_effect=RuntimeError,
    )
    daemonModel.is_running = True
    daemonModel.save(update_fields=["is_running"])

    emailArchiverDaemon.start()

    daemonModel.refresh_from_db()
    assert daemonModel.is_running is True
    mock_thread_start.assert_called_once_with(emailArchiverDaemon)
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_success(daemonModel, emailArchiverDaemon):
    daemonModel.is_running = True
    daemonModel.save(update_fields=["is_running"])

    emailArchiverDaemon.stop()

    daemonModel.refresh_from_db()
    assert daemonModel.is_running is False
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_failure(daemonModel, emailArchiverDaemon):
    emailArchiverDaemon._stopEvent.set()
    daemonModel.is_running = False
    daemonModel.save(update_fields=["is_running"])

    emailArchiverDaemon.stop()

    daemonModel.refresh_from_db()
    assert daemonModel.is_running is False
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_start_stop(mocker, daemonModel, emailArchiverDaemon):
    mock_cycle = mocker.patch(
        "core.EMailArchiverDaemon.EMailArchiverDaemon.cycle", autospec=True
    )
    mock_sleep = mocker.patch("core.EMailArchiverDaemon.time.sleep", autospec=True)
    daemonModel.is_running = False
    daemonModel.save(update_fields=["is_running"])

    emailArchiverDaemon.start()
    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    daemonModel.refresh_from_db()
    assert daemonModel.is_running is False
    assert not emailArchiverDaemon.is_alive()
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_update(daemonModel, emailArchiverDaemon):
    post_save.disconnect(post_save_daemon, DaemonModel)

    daemonModel = DaemonModel.objects.get(id=daemonModel.id)
    old_cycle_interval = daemonModel.cycle_interval
    daemonModel.cycle_interval = old_cycle_interval * 12
    daemonModel.save()
    assert emailArchiverDaemon._daemonModel.cycle_interval == old_cycle_interval

    emailArchiverDaemon.update()

    assert emailArchiverDaemon._daemonModel.cycle_interval == daemonModel.cycle_interval
    emailArchiverDaemon.logger.debug.assert_called()

    post_save.connect(post_save_daemon, DaemonModel)


@pytest.mark.django_db
def test_cycle_success(mocker, emailArchiverDaemon):
    mock_mailbox_fetch = mocker.patch(
        "core.models.MailboxModel.MailboxModel.fetch", autospec=True
    )
    emailArchiverDaemon._daemonModel.is_healthy = False
    emailArchiverDaemon._daemonModel.save(update_fields=["is_healthy"])

    emailArchiverDaemon.cycle()

    mock_mailbox_fetch.assert_called_once_with(
        emailArchiverDaemon._daemonModel.mailbox,
        emailArchiverDaemon._daemonModel.fetching_criterion,
    )
    assert emailArchiverDaemon._daemonModel.is_healthy is True
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_cycle_exception(mocker, emailArchiverDaemon):
    mock_mailbox_fetch = mocker.patch(
        "core.models.MailboxModel.MailboxModel.fetch",
        autospec=True,
        side_effect=AssertionError,
    )
    emailArchiverDaemon._daemonModel.is_healthy = False
    emailArchiverDaemon._daemonModel.save(update_fields=["is_healthy"])

    with pytest.raises(AssertionError):
        emailArchiverDaemon.cycle()

    mock_mailbox_fetch.assert_called_once_with(
        emailArchiverDaemon._daemonModel.mailbox,
        emailArchiverDaemon._daemonModel.fetching_criterion,
    )
    assert emailArchiverDaemon._daemonModel.is_healthy is False
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_run_success(mocker, emailArchiverDaemon):
    mock_cycle = mocker.patch(
        "core.EMailArchiverDaemon.EMailArchiverDaemon.cycle", autospec=True
    )
    mock_sleep = mocker.patch("core.EMailArchiverDaemon.time.sleep", autospec=True)

    emailArchiverDaemon.start()

    assert emailArchiverDaemon.is_alive()
    mock_sleep.assert_called_with(emailArchiverDaemon._daemonModel.cycle_interval)
    mock_cycle.assert_called()

    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    assert not emailArchiverDaemon.is_alive()


@pytest.mark.django_db
def test_run_exception(mocker, emailArchiverDaemon):
    mock_cycle = mocker.patch(
        "core.EMailArchiverDaemon.EMailArchiverDaemon.cycle",
        autospec=True,
        side_effect=AssertionError,
    )
    mock_sleep = mocker.patch("core.EMailArchiverDaemon.time.sleep", autospec=True)

    emailArchiverDaemon.start()

    assert emailArchiverDaemon.is_alive()
    mock_cycle.assert_called()
    emailArchiverDaemon.logger.exception.assert_called()
    mock_sleep.assert_called_with(emailArchiverDaemon._daemonModel.restart_time)
    assert emailArchiverDaemon._daemonModel.is_healthy is False

    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    assert not emailArchiverDaemon.is_alive()
