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

import pytest
from core.EMailArchiverDaemonRegistry import EMailArchiverDaemonRegistry

from .models.test_DaemonModel import fixture_daemonModel

@pytest.fixture(name='mock_logger')
def fixture_mock_logger(mocker, monkeypatch):
    mock_logger = mocker.Mock()
    mocker.patch('core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.logger', mock_logger)
    return mock_logger

@pytest.fixture(name='mock_runningDaemon')
def fixture_mock_runningDaemon(mocker, daemon):
    mock_runningDaemon = mocker.MagicMock()
    EMailArchiverDaemonRegistry._runningDaemons[daemon.id] = mock_runningDaemon
    yield mock_runningDaemon
    try:
        EMailArchiverDaemonRegistry._runningDaemons.pop(daemon.id)
    except KeyError:
        pass


@pytest.fixture(name='patch_EMailArchiverDaemon')
def fixture_patch_EMailArchiverDaemon(mocker):
    return mocker.patch('core.EMailArchiverDaemonRegistry.EMailArchiverDaemon', return_value=mocker.Mock())


@pytest.mark.django_db
def test_isRunning_active(mock_runningDaemon, daemon):
    result = EMailArchiverDaemonRegistry.isRunning(daemon)

    assert result is True


@pytest.mark.django_db
def test_isRunning_inactive(daemon):
    result = EMailArchiverDaemonRegistry.isRunning(daemon)

    assert result is False


@pytest.mark.django_db
def test_updateDaemon(mock_logger, mock_runningDaemon, daemon):
    EMailArchiverDaemonRegistry.updateDaemon(daemon)

    mock_runningDaemon.update.assert_called_once()
    mock_logger.debug.assert_called()



@pytest.mark.django_db
def test_testDaemon_success(mock_logger, patch_EMailArchiverDaemon, daemon):
    result = EMailArchiverDaemonRegistry.testDaemon(daemon)

    assert result is True
    patch_EMailArchiverDaemon.assert_called_once_with(daemon)
    patch_EMailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_testDaemon_failure_exception(mock_logger, patch_EMailArchiverDaemon, daemon):
    patch_EMailArchiverDaemon.return_value.cycle.side_effect = Exception

    result = EMailArchiverDaemonRegistry.testDaemon(daemon)

    assert result is False
    patch_EMailArchiverDaemon.assert_called_once_with(daemon)
    patch_EMailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_testDaemon_failure_unhealthy(mock_logger, patch_EMailArchiverDaemon, daemon):
    def unhealthyDaemon():
        daemon.is_healthy = False
        daemon.save(update_fields=['is_healthy'])
    patch_EMailArchiverDaemon.return_value.cycle.side_effect = unhealthyDaemon

    result = EMailArchiverDaemonRegistry.testDaemon(daemon)

    assert result is False
    patch_EMailArchiverDaemon.assert_called_once_with(daemon)
    patch_EMailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_startDaemon_active(mock_logger, patch_EMailArchiverDaemon, mock_runningDaemon, daemon):
    result = EMailArchiverDaemonRegistry.startDaemon(daemon)

    assert result is False
    patch_EMailArchiverDaemon.assert_not_called()
    patch_EMailArchiverDaemon.return_value.start.assert_not_called()
    assert daemon.id in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_startDaemon_inactive(mock_logger, patch_EMailArchiverDaemon, daemon):
    result = EMailArchiverDaemonRegistry.startDaemon(daemon)

    assert result is True
    patch_EMailArchiverDaemon.assert_called_once_with(daemon)
    patch_EMailArchiverDaemon.return_value.start.assert_called_once_with()
    assert daemon.id in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_active(mock_logger, mock_runningDaemon, daemon):
    result = EMailArchiverDaemonRegistry.stopDaemon(daemon)

    assert result is True
    mock_runningDaemon.stop.assert_called_once_with()
    assert daemon.id not in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_inactive(mock_logger, daemon):
    result = EMailArchiverDaemonRegistry.stopDaemon(daemon)

    assert result is False
    assert daemon.id not in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()
