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

import contextlib

import pytest

from core.EMailArchiverDaemon import EMailArchiverDaemon
from core.EMailArchiverDaemonRegistry import EMailArchiverDaemonRegistry


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    return mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.logger",
        autospec=True,
    )


@pytest.fixture
def mock_runningDaemon(mocker, daemonModel):
    mock_runningDaemon = mocker.MagicMock()
    EMailArchiverDaemonRegistry._runningDaemons[daemonModel.id] = mock_runningDaemon
    yield mock_runningDaemon
    with contextlib.suppress(KeyError):
        EMailArchiverDaemonRegistry._runningDaemons.pop(daemonModel.id)


@pytest.fixture
def mock_EMailArchiverDaemon(mocker):
    return mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemon",
        autospec=True,
        return_value=mocker.Mock(spec=EMailArchiverDaemon),
    )


@pytest.mark.django_db
def test_isRunning_active(mock_runningDaemon, daemonModel):
    result = EMailArchiverDaemonRegistry.isRunning(daemonModel)

    assert result is True


@pytest.mark.django_db
def test_isRunning_inactive(daemonModel):
    result = EMailArchiverDaemonRegistry.isRunning(daemonModel)

    assert result is False


@pytest.mark.django_db
def test_updateDaemon(mock_logger, mock_runningDaemon, daemonModel):
    EMailArchiverDaemonRegistry.updateDaemon(daemonModel)

    mock_runningDaemon.update.assert_called_once()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_testDaemon_success(mock_logger, mock_EMailArchiverDaemon, daemonModel):
    result = EMailArchiverDaemonRegistry.testDaemon(daemonModel)

    assert result is True
    mock_EMailArchiverDaemon.assert_called_once_with(daemonModel)
    mock_EMailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_testDaemon_failure_exception(
    mock_logger, mock_EMailArchiverDaemon, daemonModel
):
    mock_EMailArchiverDaemon.return_value.cycle.side_effect = Exception

    result = EMailArchiverDaemonRegistry.testDaemon(daemonModel)

    assert result is False
    mock_EMailArchiverDaemon.assert_called_once_with(daemonModel)
    mock_EMailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_startDaemon_active(
    mock_logger, mock_EMailArchiverDaemon, mock_runningDaemon, daemonModel
):
    result = EMailArchiverDaemonRegistry.startDaemon(daemonModel)

    assert result is False
    mock_EMailArchiverDaemon.assert_not_called()
    mock_EMailArchiverDaemon.return_value.start.assert_not_called()
    assert daemonModel.id in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_startDaemon_inactive(mock_logger, mock_EMailArchiverDaemon, daemonModel):
    result = EMailArchiverDaemonRegistry.startDaemon(daemonModel)

    assert result is True
    mock_EMailArchiverDaemon.assert_called_once_with(daemonModel)
    mock_EMailArchiverDaemon.return_value.start.assert_called_once_with()
    assert daemonModel.id in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_active(mock_logger, mock_runningDaemon, daemonModel):
    result = EMailArchiverDaemonRegistry.stopDaemon(daemonModel)

    assert result is True
    mock_runningDaemon.stop.assert_called_once_with()
    assert daemonModel.id not in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_inactive(mock_logger, daemonModel):
    result = EMailArchiverDaemonRegistry.stopDaemon(daemonModel)

    assert result is False
    assert daemonModel.id not in EMailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()
