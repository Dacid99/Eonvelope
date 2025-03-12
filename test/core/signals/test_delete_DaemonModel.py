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

"""Test module for :mod:`core.signals.delete_DaemonModel`."""

import pytest

from core.models.DaemonModel import DaemonModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_AccountModel.logger` of the module."""
    return mocker.patch("core.signals.delete_DaemonModel.logger", autospec=True)


@pytest.mark.django_db
def test_pre_delete_stop_daemon(mocker, mock_logger, daemonModel):
    """Tests :func:`core.signals.deleteDaemonModel.pre_delete_stop_daemon`."""
    mock_EMailArchiverDaemon_stopDaemon = mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.stopDaemon",
        autospec=True,
    )

    daemonModel.delete()

    with pytest.raises(DaemonModel.DoesNotExist):
        daemonModel.refresh_from_db()
    mock_EMailArchiverDaemon_stopDaemon.assert_called_once()
    mock_logger.debug.assert_called()
