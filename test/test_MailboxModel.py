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


"""Test module for :mod:`Emailkasten.Models.MailboxModel`."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError

from .ModelFactories.MailboxModelFactory import MailboxModelFactory
from .ModelFactories.DaemonModelFactory import DaemonModelFactory
from .ModelFactories.UserFactory import UserFactory

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock.plugin import MockerFixture


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mocks :attr:`Emailkasten.fileManagment.logger` of the module."""
    return mocker.patch('Emailkasten.Models.MailboxModel.logger')


@pytest.mark.django_db
def MailboxModel_creation():
    """Tests the correct creation of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    mailbox = MailboxModelFactory()
    assert mailbox.mail_host_port is None
    assert mailbox.timeout is None
    assert mailbox.is_healthy is True
    assert mailbox.is_favorite is False
    assert isinstance(mailbox.updated, datetime.datetime)
    assert mailbox.updated is not None
    assert isinstance(mailbox.created, datetime.datetime)
    assert mailbox.created is not None
    assert mailbox.mail_address in str(mailbox)
    assert mailbox.mail_host in str(mailbox)
    assert mailbox.protocol in str(mailbox)


@pytest.mark.django_db
def MailboxModel_unique():
    """Tests the uniqie constraints of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    mailingList_1 = MailboxModelFactory(mail_address="abc123")
    mailingList_2 = MailboxModelFactory(mail_address="abc123")
    assert mailingList_1.mail_address == mailingList_2.mail_address
    assert mailingList_1.user != mailingList_2.user

    user = UserFactory()

    mailingList_1 = MailboxModelFactory(user = user)
    mailingList_2 = MailboxModelFactory(user = user)
    assert mailingList_1.mail_address != mailingList_2.mail_address
    assert mailingList_1.user == mailingList_2.user

    MailboxModelFactory(mail_address="abc123", user = user)
    with pytest.raises(IntegrityError):
        MailboxModelFactory(mail_address="abc123", user = user)


@pytest.mark.django_db
def test_MailboxModel_post_save(mock_logger):
    mailbox = MailboxModelFactory()
    daemon = DaemonModelFactory(mailbox=mailbox)
    mock_logger.debug.assert_called()

    assert mailbox.account.is_healthy is True

    mailbox.is_healthy = False
    mailbox.save(update_fields = ['is_healthy'])
    daemons = mailbox.daemons.all()
    for daemon in daemons:
        assert daemon.is_healthy is False
    mock_logger.debug.assert_called()

    mailbox.is_healthy = True
    mailbox.save(update_fields = ['is_healthy'])
    assert mailbox.account.is_healthy is True
    mock_logger.debug.assert_called()
