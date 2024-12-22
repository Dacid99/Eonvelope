# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pytest

import Emailkasten.EMailArchiverDaemon

from .ModelFactories.DaemonModelFactory import DaemonModelFactory


@pytest.fixture(name='mock_getLogger', autouse=True)
def fixture_mock_getLogger(mocker):
    mock_logger = mocker.patch('Emailkasten.EMailArchiverDaemon.logging.Logger')
    return mocker.patch('Emailkasten.EMailArchiverDaemon.logging.getLogger', return_value = mock_logger)

@pytest.fixture(name='mock_runningDaemons')
def fixture_mock_runningDaemons():
    return {}


@pytest.mark.django_db
@pytest.fixture(name='mock_daemonModel')
def fixture_mock_daemonModel():
    return DaemonModelFactory()


@pytest.mark.django_db
def test___init__(mock_daemonModel):
    daemonInstance = Emailkasten.EMailArchiverDaemon.EMailArchiverDaemon(mock_daemonModel)
    assert daemonInstance.thread is None
    assert daemonInstance is not None
    assert daemonInstance.isRunning is False


@pytest.mark.parametrize(
    'is_running',
    [
        True,
        False
    ]
)
@pytest.mark.django_db
def test_start(mocker, is_running):
    mock_threading = mocker.patch('Emailkasten.EMailArchiverDaemon.threading.Thread')
    daemonEntry = DaemonModelFactory(is_running = is_running)
    daemonInstance = Emailkasten.EMailArchiverDaemon.EMailArchiverDaemon(daemonEntry)
    daemonInstance.isRunning = is_running

    daemonInstance.start()

    assert daemonEntry.is_running is True
    assert daemonInstance.isRunning is True
    mock_threading.assert_called_once()
    assert mock_threading.start.call_count == 1 if is_running else 0

    daemonInstance.logger.info.assert_called()
