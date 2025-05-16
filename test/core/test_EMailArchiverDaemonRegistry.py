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

from core.EmailArchiverDaemon import EmailArchiverDaemon
from core.EmailArchiverDaemonRegistry import EmailArchiverDaemonRegistry


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    return mocker.patch(
        "core.EmailArchiverDaemonRegistry.EmailArchiverDaemonRegistry.logger",
        autospec=True,
    )


@pytest.fixture
def mock_runningDaemon(mocker, fake_daemon):
    mock_runningDaemon = mocker.MagicMock()
    EmailArchiverDaemonRegistry._runningDaemons[fake_daemon.id] = mock_runningDaemon
    yield mock_runningDaemon
    with contextlib.suppress(KeyError):
        EmailArchiverDaemonRegistry._runningDaemons.pop(fake_daemon.id)


@pytest.fixture
def mock_EmailArchiverDaemon(mocker):
    return mocker.patch(
        "core.EmailArchiverDaemonRegistry.EmailArchiverDaemon",
        autospec=True,
        return_value=mocker.Mock(spec=EmailArchiverDaemon),
    )


@pytest.mark.django_db
def test_isRunning_active(mock_runningDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.isRunning(fake_daemon)

    assert result is True


@pytest.mark.django_db
def test_isRunning_inactive(fake_daemon):
    result = EmailArchiverDaemonRegistry.isRunning(fake_daemon)

    assert result is False


@pytest.mark.django_db
def test_updateDaemon(mock_logger, mock_runningDaemon, fake_daemon):
    EmailArchiverDaemonRegistry.updateDaemon(fake_daemon)

    mock_runningDaemon.update.assert_called_once()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_testDaemon_success(mock_logger, mock_EmailArchiverDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.testDaemon(fake_daemon)

    assert result is True
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_testDaemon_failure_exception(
    mock_logger, mock_EmailArchiverDaemon, fake_daemon
):
    mock_EmailArchiverDaemon.return_value.cycle.side_effect = Exception

    result = EmailArchiverDaemonRegistry.testDaemon(fake_daemon)

    assert result is False
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_startDaemon_active(
    mock_logger, mock_EmailArchiverDaemon, mock_runningDaemon, fake_daemon
):
    result = EmailArchiverDaemonRegistry.startDaemon(fake_daemon)

    assert result is False
    mock_EmailArchiverDaemon.assert_not_called()
    mock_EmailArchiverDaemon.return_value.start.assert_not_called()
    assert fake_daemon.id in EmailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_startDaemon_inactive(mock_logger, mock_EmailArchiverDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.startDaemon(fake_daemon)

    assert result is True
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.start.assert_called_once_with()
    assert fake_daemon.id in EmailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_active(mock_logger, mock_runningDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.stopDaemon(fake_daemon)

    assert result is True
    mock_runningDaemon.stop.assert_called_once_with()
    assert fake_daemon.id not in EmailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stopDaemon_inactive(mock_logger, fake_daemon):
    result = EmailArchiverDaemonRegistry.stopDaemon(fake_daemon)

    assert result is False
    assert fake_daemon.id not in EmailArchiverDaemonRegistry._runningDaemons
    mock_logger.debug.assert_called()
