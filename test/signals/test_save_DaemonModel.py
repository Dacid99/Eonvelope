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

"""Test file for :mod:`Emailkasten.signals.save_DaemonModel`."""

import pytest
from faker import Faker
from model_bakery import baker

from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.MailboxModel import MailboxModel


@pytest.fixture(name='mock_updateDaemon')
def fixture_mock_updateDaemon(mocker):
    return mocker.patch('Emailkasten.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.updateDaemon')

@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`Emailkasten.signals.save_DaemonModel.logger` of the module."""
    return mocker.patch('Emailkasten.signals.save_DaemonModel.logger')


@pytest.mark.django_db
def test_MailboxModel_post_save_daemon_from_healthy(mock_logger, mock_updateDaemon):
    """Tests behaviour of :func:`Emailkasten.signals.saveMailboxModel.post_save_is_healthy`."""
    mailbox = baker.make(MailboxModel, is_healthy=True)
    daemon = baker.make(DaemonModel, mailbox=mailbox, is_healthy=True, log_filepath=Faker().file_path(extension='log'))

    daemon.is_healthy = False
    daemon.save(update_fields = ['is_healthy'])

    mailbox.refresh_from_db()
    mock_updateDaemon.assert_called_once_with(daemon)
    assert mailbox.is_healthy is True
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_MailboxModel_post_save_daemon_from_unhealthy(mock_logger, mock_updateDaemon):
    """Tests behaviour of :func:`Emailkasten.signals.saveMailboxModel.post_save_is_healthy`."""
    mailbox = baker.make(MailboxModel, is_healthy=False)
    daemon = baker.make(DaemonModel, mailbox=mailbox, is_healthy=False, log_filepath=Faker().file_path(extension='log'))

    daemon.is_healthy = True
    daemon.save(update_fields = ['is_healthy'])

    mailbox.refresh_from_db()
    mock_updateDaemon.assert_called_once_with(daemon)
    assert mailbox.is_healthy is True
    mock_logger.debug.assert_called()
