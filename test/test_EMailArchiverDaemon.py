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

import pytest
from django.db.models.signals import post_save
from core.signals.save_DaemonModel import post_save_daemon
from core.EMailArchiverDaemon import EMailArchiverDaemon
from core.models.DaemonModel import DaemonModel

from .models.test_DaemonModel import fixture_mock_open
from .models.test_DaemonModel import fixture_daemonModel


@pytest.fixture(name='mock_setupLogger')
def fixture_setupLogger(mocker):
    return mocker.patch('core.EMailArchiverDaemon.EMailArchiverDaemon._setupLogger')

@pytest.fixture(name='emailArchiverDaemon')
def fixture_emailArchiverDaemon(mocker, daemon, mock_setupLogger):
    emailArchiverDaemon = EMailArchiverDaemon(daemonModel=daemon)
    emailArchiverDaemon.logger = mocker.Mock()
    return emailArchiverDaemon


@pytest.mark.django_db
def test___init__(mock_setupLogger, daemon):
    daemonInstance = EMailArchiverDaemon(daemon)
    assert daemonInstance is not None
    assert daemonInstance.daemon
    assert str(daemon.uuid) in daemonInstance.name
    assert daemonInstance._daemonModel == daemon
    assert daemonInstance._stopEvent is not None
    assert not daemonInstance._stopEvent.is_set()
    mock_setupLogger.assert_called_once_with()


@pytest.mark.django_db
def test_setupLogger(mocker, daemon):
    mock_getLogger = mocker.patch('logging.getLogger', return_value=mocker.Mock())
    mock_FileHandler = mocker.patch('logging.handlers.RotatingFileHandler', return_value=mocker.Mock())

    emailArchiverDaemon = EMailArchiverDaemon(daemonModel=daemon)

    mock_getLogger.assert_called_once()
    mock_FileHandler.assert_called_once_with(filename=daemon.log_filepath, backupCount=daemon.log_backup_count, maxBytes=daemon.logfile_size)
    mock_getLogger.return_value.addHandler.assert_called_once_with(mock_FileHandler.return_value)



@pytest.mark.django_db
def test_start_dryrun_success(mocker, daemon, emailArchiverDaemon):
    mock_thread_start = mocker.patch('core.EMailArchiverDaemon.threading.Thread.start')
    daemon.is_running = False
    daemon.save(update_fields=['is_running'])

    emailArchiverDaemon.start()

    daemon.refresh_from_db()
    assert daemon.is_running is True
    mock_thread_start.assert_called_once_with()
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_start_dryrun_failure(mocker, daemon, emailArchiverDaemon):
    mock_thread_start = mocker.patch('core.EMailArchiverDaemon.threading.Thread.start', side_effect=RuntimeError)
    daemon.is_running = True
    daemon.save(update_fields=['is_running'])

    emailArchiverDaemon.start()

    daemon.refresh_from_db()
    assert daemon.is_running is True
    mock_thread_start.assert_called_once_with()
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_success(daemon, emailArchiverDaemon):
    daemon.is_running = True
    daemon.save(update_fields=['is_running'])

    emailArchiverDaemon.stop()

    daemon.refresh_from_db()
    assert daemon.is_running is False
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_failure(daemon, emailArchiverDaemon):
    emailArchiverDaemon._stopEvent.set()
    daemon.is_running = False
    daemon.save(update_fields=['is_running'])

    emailArchiverDaemon.stop()

    daemon.refresh_from_db()
    assert daemon.is_running is False
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_start_stop(mocker, daemon, emailArchiverDaemon):
    mock_cycle = mocker.patch('core.EMailArchiverDaemon.EMailArchiverDaemon.cycle')
    mock_sleep = mocker.patch('core.EMailArchiverDaemon.time.sleep')
    daemon.is_running = False
    daemon.save(update_fields=['is_running'])

    emailArchiverDaemon.start()
    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    daemon.refresh_from_db()
    assert daemon.is_running is False
    assert not emailArchiverDaemon.is_alive()
    emailArchiverDaemon.logger.info.assert_called()


@pytest.mark.django_db
def test_update(daemon, emailArchiverDaemon):
    post_save.disconnect(post_save_daemon, DaemonModel)

    daemonModel = DaemonModel.objects.get(id=daemon.id)
    old_cycle_interval = daemonModel.cycle_interval
    daemonModel.cycle_interval = old_cycle_interval * 12
    daemonModel.save()
    assert emailArchiverDaemon._daemonModel.cycle_interval == old_cycle_interval

    emailArchiverDaemon.update()

    assert emailArchiverDaemon._daemonModel.cycle_interval == daemon.cycle_interval
    emailArchiverDaemon.logger.debug.assert_called()

    post_save.connect(post_save_daemon, DaemonModel)


@pytest.mark.django_db
def test_cycle_success(mocker, emailArchiverDaemon):
    mock_fetchAndProcessMails = mocker.patch('core.EMailArchiverDaemon.fetchAndProcessMails')
    emailArchiverDaemon._daemonModel.is_healthy = False
    emailArchiverDaemon._daemonModel.save(update_fields=['is_healthy'])

    emailArchiverDaemon.cycle()

    mock_fetchAndProcessMails.assert_called_once_with(emailArchiverDaemon._daemonModel.mailbox, emailArchiverDaemon._daemonModel.fetching_criterion)
    assert emailArchiverDaemon._daemonModel.is_healthy is True
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_cycle_exception(mocker, emailArchiverDaemon):
    mock_fetchAndProcessMails = mocker.patch('core.EMailArchiverDaemon.fetchAndProcessMails', side_effect=Exception)
    emailArchiverDaemon._daemonModel.is_healthy = False
    emailArchiverDaemon._daemonModel.save(update_fields=['is_healthy'])

    with pytest.raises(Exception):
        emailArchiverDaemon.cycle()

    mock_fetchAndProcessMails.assert_called_once_with(emailArchiverDaemon._daemonModel.mailbox, emailArchiverDaemon._daemonModel.fetching_criterion)
    assert emailArchiverDaemon._daemonModel.is_healthy is False
    emailArchiverDaemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_run_success(mocker, emailArchiverDaemon):
    mock_cycle = mocker.patch('core.EMailArchiverDaemon.EMailArchiverDaemon.cycle')
    mock_sleep = mocker.patch('core.EMailArchiverDaemon.time.sleep')

    emailArchiverDaemon.start()

    assert emailArchiverDaemon.is_alive()
    mock_sleep.assert_called_with(emailArchiverDaemon._daemonModel.cycle_interval)
    mock_cycle.assert_called()

    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    assert not emailArchiverDaemon.is_alive()


@pytest.mark.django_db
def test_run_exception(mocker, emailArchiverDaemon):
    mock_cycle = mocker.patch('core.EMailArchiverDaemon.EMailArchiverDaemon.cycle', side_effect=Exception)
    mock_sleep = mocker.patch('core.EMailArchiverDaemon.time.sleep')

    emailArchiverDaemon.start()

    assert emailArchiverDaemon.is_alive()
    mock_cycle.assert_called()
    emailArchiverDaemon.logger.error.assert_called()
    mock_sleep.assert_called_with(emailArchiverDaemon._daemonModel.restart_time)
    assert emailArchiverDaemon._daemonModel.is_healthy is False

    emailArchiverDaemon.stop()
    emailArchiverDaemon.join()

    assert not emailArchiverDaemon.is_alive()
