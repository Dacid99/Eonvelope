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

"""Test file for :mod:`core.signals.save_MailboxModel`."""

import pytest
from model_bakery import baker

from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Mocks :attr:`core.signals.save_MailboxModel.logger` of the module."""
    return mocker.patch("core.signals.save_MailboxModel.logger", autospec=True)


@pytest.mark.django_db
def test_MailboxModel_post_save_from_healthy(mailboxModel_with_daemons, mock_logger):
    """Tests behaviour of :func:`core.signals.saveMailboxModel.post_save_is_healthy`."""
    mailboxModel_with_daemons.account.is_healthy = True
    mailboxModel_with_daemons.account.save(update_fields=["is_healthy"])
    mailboxModel_with_daemons.is_healthy = True
    mailboxModel_with_daemons.save(update_fields=["is_healthy"])
    for daemon in mailboxModel_with_daemons.daemons.all():
        daemon.is_healthy = True
        daemon.save(update_fields=["is_healthy"])

    mailboxModel_with_daemons.refresh_from_db()
    assert mailboxModel_with_daemons.is_healthy is True
    mailboxModel_with_daemons.account.refresh_from_db()
    assert mailboxModel_with_daemons.account.is_healthy is True
    for daemon in mailboxModel_with_daemons.daemons.all():
        assert daemon.is_healthy is True

    mailboxModel_with_daemons.is_healthy = False
    mailboxModel_with_daemons.save(update_fields=["is_healthy"])

    mailboxModel_with_daemons.refresh_from_db()
    assert mailboxModel_with_daemons.is_healthy is False
    mailboxModel_with_daemons.account.refresh_from_db()
    assert mailboxModel_with_daemons.account.is_healthy is True
    for daemon in mailboxModel_with_daemons.daemons.all():
        assert daemon.is_healthy is False
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_MailboxModel_post_save_from_unhealthy(mailboxModel_with_daemons, mock_logger):
    """Tests behaviour of :func:`core.signals.saveMailboxModel.post_save_is_healthy`."""
    mailboxModel_with_daemons.account.is_healthy = False
    mailboxModel_with_daemons.account.save(update_fields=["is_healthy"])
    mailboxModel_with_daemons.is_healthy = False
    mailboxModel_with_daemons.save(update_fields=["is_healthy"])
    for daemon in mailboxModel_with_daemons.daemons.all():
        daemon.is_healthy = False
        daemon.save(update_fields=["is_healthy"])

    mailboxModel_with_daemons.refresh_from_db()
    assert mailboxModel_with_daemons.is_healthy is False
    mailboxModel_with_daemons.account.refresh_from_db()
    assert mailboxModel_with_daemons.account.is_healthy is False
    for daemon in mailboxModel_with_daemons.daemons.all():
        assert daemon.is_healthy is False

    mailboxModel_with_daemons.is_healthy = True
    mailboxModel_with_daemons.save(update_fields=["is_healthy"])

    mailboxModel_with_daemons.refresh_from_db()
    assert mailboxModel_with_daemons.is_healthy is True
    mailboxModel_with_daemons.account.refresh_from_db()
    assert mailboxModel_with_daemons.account.is_healthy is True
    for daemon in mailboxModel_with_daemons.daemons.all():
        assert daemon.is_healthy is False
    mock_logger.debug.assert_called()
