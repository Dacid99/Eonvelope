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

"""Test file for :mod:`core.signals.save_Daemon`."""

import pytest


@pytest.fixture
def mock_updateDaemon(mocker):
    """Patches the :func:`core.EmailArchiverDaemonRegistry.EmailArchiverDaemonRegistry.updateDaemon`
    function called in the signal.
    """
    return mocker.patch(
        "core.EmailArchiverDaemonRegistry.EmailArchiverDaemonRegistry.updateDaemon",
        autospec=True,
    )


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_Daemon.logger` of the module."""
    return mocker.patch("core.signals.save_Daemon.logger", autospec=True)


@pytest.mark.django_db
def test_Daemon_post_save_from_healthy(fake_daemon, mock_logger, mock_updateDaemon):
    """Tests :func:`core.signals.saveDaemon.post_save_is_healthy`
    for an initially healthy daemon.
    """
    fake_daemon.is_healthy = True
    fake_daemon.save(update_fields=["is_healthy"])
    fake_daemon.mailbox.is_healthy = True
    fake_daemon.mailbox.save(update_fields=["is_healthy"])

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_healthy is True
    fake_daemon.mailbox.refresh_from_db()
    assert fake_daemon.mailbox.is_healthy is True

    fake_daemon.is_healthy = False
    fake_daemon.save(update_fields=["is_healthy"])

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_healthy is False
    fake_daemon.mailbox.refresh_from_db()
    assert fake_daemon.mailbox.is_healthy is True
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_Daemon_post_save_from_unhealthy(fake_daemon, mock_logger, mock_updateDaemon):
    """Tests :func:`core.signals.saveDaemon.post_save_is_healthy`
    for an initially unhealthy daemon.
    """
    fake_daemon.is_healthy = False
    fake_daemon.save(update_fields=["is_healthy"])
    fake_daemon.mailbox.is_healthy = False
    fake_daemon.mailbox.save(update_fields=["is_healthy"])

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_healthy is False
    fake_daemon.mailbox.refresh_from_db()
    assert fake_daemon.mailbox.is_healthy is False

    fake_daemon.is_healthy = True
    fake_daemon.save(update_fields=["is_healthy"])

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_healthy is True
    fake_daemon.mailbox.refresh_from_db()
    assert fake_daemon.mailbox.is_healthy is True
    mock_logger.debug.assert_called()
