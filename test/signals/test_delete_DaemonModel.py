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
from ..models.test_DaemonModel import fixture_daemonModel
from Emailkasten.Models.DaemonModel import DaemonModel

@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`Emailkasten.signals.save_AccountModel.logger` of the module."""
    return mocker.patch('Emailkasten.signals.delete_DaemonModel.logger')

@pytest.mark.django_db
def test_pre_delete_stop_daemon(mocker, mock_logger, daemon):
    mock_EMailArchiverDaemon_stopDaemon = mocker.patch('Emailkasten.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.stopDaemon')

    daemon.delete()

    with pytest.raises(DaemonModel.DoesNotExist):
        daemon.refresh_from_db()
    mock_EMailArchiverDaemon_stopDaemon.assert_called_once()
    mock_logger.debug.assert_called()
