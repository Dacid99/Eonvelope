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

import datetime

import pytest
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten import constants
from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.MailboxModel import MailboxModel


@pytest.mark.django_db
def MailboxModel_creation():
    """Tests the correct default creation of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    mailbox = baker.make(MailboxModel)
    assert mailbox.name is not None
    assert mailbox.account is not None
    assert mailbox.save_attachments is constants.FetchingConfiguration.SAVE_ATTACHMENTS_DEFAULT
    assert mailbox.save_images is constants.FetchingConfiguration.SAVE_IMAGES_DEFAULT
    assert mailbox.save_toEML is constants.FetchingConfiguration.SAVE_TO_EML_DEFAULT
    assert mailbox.is_favorite is False
    assert mailbox.is_healthy is True
    assert isinstance(mailbox.updated, datetime.datetime)
    assert mailbox.updated is not None
    assert isinstance(mailbox.created, datetime.datetime)
    assert mailbox.created is not None

    assert mailbox.name in str(mailbox)
    assert str(mailbox.account) in str(mailbox)


@pytest.mark.django_db
def MailboxModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    mailingList_1 = baker.make(MailboxModel, name="abc123")
    mailingList_2 = baker.make(MailboxModel, name="abc123")
    assert mailingList_1.name == mailingList_2.name
    assert mailingList_1.account != mailingList_2.account

    account = baker.maker(AccountModel)

    mailingList_1 = baker.make(MailboxModel, account = account)
    mailingList_2 = baker.make(MailboxModel, account = account)
    assert mailingList_1.name != mailingList_2.name
    assert mailingList_1.account == mailingList_2.account

    baker.make(MailboxModel, name="abc123", account = account)
    with pytest.raises(IntegrityError):
        baker.make(MailboxModel, name="abc123", account = account)


@pytest.mark.django_db
def test_MailboxModel_post_save():
    mailbox = baker.make(MailboxModel)
    daemon_1 = baker.make(DaemonModel, mailbox=mailbox)
    daemon_2 = baker.make(DaemonModel, mailbox=mailbox)

    assert mailbox.account.is_healthy is True

    mailbox.is_healthy = False
    mailbox.save(update_fields = ['is_healthy'])
    daemons = mailbox.daemons.all()
    for daemon in daemons:
        assert daemon.is_healthy is False

    mailbox.is_healthy = True
    mailbox.save(update_fields = ['is_healthy'])
    for daemon in daemons:
        daemon.refresh_from_db()
        assert daemon.is_healthy is False
