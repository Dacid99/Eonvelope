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


"""Test module for :mod:`Emailkasten.Models.AccountModel`."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError

from .ModelFactories.AccountModelFactory import AccountModelFactory
from .ModelFactories.MailboxModelFactory import MailboxModelFactory
from .ModelFactories.UserFactory import UserFactory

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock.plugin import MockerFixture


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker: MockerFixture) -> MagicMock:
    """Mocks :attr:`Emailkasten.fileManagment.logger` of the module."""
    return mocker.patch('Emailkasten.Models.AccountModel.logger')


@pytest.mark.django_db
def test_AccountModel_creation():
    """Tests the correct creation of :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    account = AccountModelFactory()
    assert account.mail_host_port is None
    assert account.timeout is None
    assert account.is_healthy is True
    assert account.is_favorite is False
    assert isinstance(account.updated, datetime.datetime)
    assert account.updated is not None
    assert isinstance(account.created, datetime.datetime)
    assert account.created is not None
    assert account.mail_address in str(account)
    assert account.mail_host in str(account)
    assert account.protocol in str(account)


@pytest.mark.django_db
def test_AccountModel_unique():
    """Tests the uniqie constraints of :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    mailingList_1 = AccountModelFactory(mail_address="abc123")
    mailingList_2 = AccountModelFactory(mail_address="abc123")
    assert mailingList_1.mail_address == mailingList_2.mail_address
    assert mailingList_1.user != mailingList_2.user

    user = UserFactory()

    mailingList_1 = AccountModelFactory(user = user)
    mailingList_2 = AccountModelFactory(user = user)
    assert mailingList_1.mail_address != mailingList_2.mail_address
    assert mailingList_1.user == mailingList_2.user

    AccountModelFactory(mail_address="abc123", user = user)
    with pytest.raises(IntegrityError):
        AccountModelFactory(mail_address="abc123", user = user)


@pytest.mark.django_db
def test_AccountModel_post_save(mock_logger):
    account = AccountModelFactory()
    mock_logger.debug.assert_called()

    mailbox_1 = MailboxModelFactory(account=account)
    mailbox_2 = MailboxModelFactory(account=account)

    assert mailbox_1.is_healthy is True
    assert mailbox_2.is_healthy is True

    account.is_healthy = False
    account.save()
    assert mailbox_1.is_healthy is False
    assert mailbox_2.is_healthy is False
    mock_logger.debug.assert_called()

    account.is_healthy = True
    account.save(update_fields = ['is_healthy'])
    assert mailbox_1.is_healthy is False
    assert mailbox_2.is_healthy is False
    mock_logger.debug.assert_not_called()
