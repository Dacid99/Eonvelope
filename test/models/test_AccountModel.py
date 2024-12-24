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

"""Test module for :mod:`Emailkasten.Models.AccountModel`."""

import datetime

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten.Models.AccountModel import AccountModel


@pytest.mark.django_db
def test_AccountModel_creation():
    """Tests the correct default creation of :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    account = baker.make(AccountModel)
    assert account.mail_address is not None
    assert isinstance(account.mail_address, str)
    assert account.password is not None
    assert isinstance(account.password, str)
    assert account.mail_host is not None
    assert isinstance(account.mail_host, str)
    assert account.mail_host_port is None
    assert account.protocol is not None
    assert isinstance(account.protocol, str)
    assert any(
        account.protocol == protocol for protocol, _ in AccountModel.PROTOCOL_CHOICES
    )
    assert account.timeout is None
    assert account.is_healthy is True
    assert account.is_favorite is False
    assert account.user is not None
    assert isinstance(account.user, User)
    assert account.updated is not None
    assert isinstance(account.updated, datetime.datetime)
    assert account.created is not None
    assert isinstance(account.created, datetime.datetime)

    assert account.mail_address in str(account)
    assert account.mail_host in str(account)
    assert account.protocol in str(account)


@pytest.mark.django_db
def test_AccountModel_foreign_key_deletion():
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    user = baker.make(User)
    account = baker.make(AccountModel, user = user)
    assert account is not None
    user.delete()
    with pytest.raises(AccountModel.DoesNotExist):
        account.refresh_from_db()


@pytest.mark.django_db
def test_AccountModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.AccountModel.AccountModel`."""

    account_1 = baker.make(AccountModel, mail_address="abc123")
    account_2 = baker.make(AccountModel, mail_address="abc123")
    assert account_1.mail_address == account_2.mail_address
    assert account_1.user != account_2.user

    user = baker.make(User)

    account_1 = baker.make(AccountModel, user = user)
    account_2 = baker.make(AccountModel, user = user)
    assert account_1.mail_address != account_2.mail_address
    assert account_1.user == account_2.user

    baker.make(AccountModel, mail_address="abc123", user = user)
    with pytest.raises(IntegrityError):
        baker.make(AccountModel, mail_address="abc123", user = user)
