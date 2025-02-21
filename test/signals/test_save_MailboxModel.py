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

from core.models.AccountModel import AccountModel
from core.models.DaemonModel import DaemonModel
from core.models.MailboxModel import MailboxModel


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`core.signals.save_MailboxModel.logger` of the module."""
    return mocker.patch("core.signals.save_MailboxModel.logger")


@pytest.mark.django_db
def test_MailboxModel_post_save_from_healthy(faker, mock_logger):
    """Tests behaviour of :func:`core.signals.saveMailboxModel.post_save_is_healthy`."""
    account = baker.make(AccountModel, is_healthy=True)
    mailbox = baker.make(MailboxModel, account=account, is_healthy=True)
    baker.make(
        DaemonModel,
        mailbox=mailbox,
        is_healthy=True,
        log_filepath=faker.file_path(extension="log"),
    )
    baker.make(
        DaemonModel,
        mailbox=mailbox,
        is_healthy=True,
        log_filepath=faker.file_path(extension="log"),
    )

    mailbox.is_healthy = False
    mailbox.save(update_fields=["is_healthy"])
    for daemon in mailbox.daemons.all():
        assert daemon.is_healthy is False
    account.refresh_from_db()
    assert account.is_healthy is True
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_MailboxModel_post_save_from_unhealthy(faker, mock_logger):
    """Tests behaviour of :func:`core.signals.saveMailboxModel.post_save_is_healthy`."""
    account = baker.make(AccountModel, is_healthy=False)
    mailbox = baker.make(MailboxModel, account=account, is_healthy=False)
    baker.make(
        DaemonModel,
        mailbox=mailbox,
        is_healthy=False,
        log_filepath=faker.file_path(extension="log"),
    )
    baker.make(
        DaemonModel,
        mailbox=mailbox,
        is_healthy=False,
        log_filepath=faker.file_path(extension="log"),
    )

    mailbox.is_healthy = True
    mailbox.save(update_fields=["is_healthy"])
    for daemon in mailbox.daemons.all():
        assert daemon.is_healthy is False
    account.refresh_from_db()
    assert account.is_healthy is True
    mock_logger.debug.assert_called()
