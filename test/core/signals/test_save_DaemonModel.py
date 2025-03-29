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

"""Test file for :mod:`core.signals.save_DaemonModel`."""

import pytest
from model_bakery import baker

from core.models.DaemonModel import DaemonModel


@pytest.fixture
def mock_updateDaemon(mocker):
    """Patches the :func:`core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.updateDaemon`
    function called in the signal.
    """
    return mocker.patch(
        "core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.updateDaemon",
        autospec=True,
    )


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_DaemonModel.logger` of the module."""
    return mocker.patch("core.signals.save_DaemonModel.logger", autospec=True)


@pytest.mark.django_db
def test_DaemonModel_post_save_from_healthy(
    daemonModel, mock_logger, mock_updateDaemon
):
    """Tests :func:`core.signals.saveDaemonModel.post_save_is_healthy`
    for an initially healthy daemon.
    """
    daemonModel.is_healthy = True
    daemonModel.save(update_fields=["is_healthy"])
    daemonModel.mailbox.is_healthy = True
    daemonModel.mailbox.save(update_fields=["is_healthy"])

    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is True
    daemonModel.mailbox.refresh_from_db()
    assert daemonModel.mailbox.is_healthy is True

    daemonModel.is_healthy = False
    daemonModel.save(update_fields=["is_healthy"])

    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is False
    daemonModel.mailbox.refresh_from_db()
    assert daemonModel.mailbox.is_healthy is True
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_DaemonModel_post_save_from_unhealthy(
    daemonModel, mock_logger, mock_updateDaemon
):
    """Tests :func:`core.signals.saveDaemonModel.post_save_is_healthy`
    for an initially unhealthy daemon.
    """
    daemonModel.is_healthy = False
    daemonModel.save(update_fields=["is_healthy"])
    daemonModel.mailbox.is_healthy = False
    daemonModel.mailbox.save(update_fields=["is_healthy"])

    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is False
    daemonModel.mailbox.refresh_from_db()
    assert daemonModel.mailbox.is_healthy is False

    daemonModel.is_healthy = True
    daemonModel.save(update_fields=["is_healthy"])

    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is True
    daemonModel.mailbox.refresh_from_db()
    assert daemonModel.mailbox.is_healthy is True
    mock_logger.debug.assert_called()
