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
@pytest.mark.parametrize(
        'protocol, expectedFetchingCriteria',
        [
            (IMAPFetcher.PROTOCOL, IMAPFetcher.AVAILABLE_FETCHING_CRITERIA),
            (POP3Fetcher.PROTOCOL, POP3Fetcher.AVAILABLE_FETCHING_CRITERIA),
            (IMAP_SSL_Fetcher.PROTOCOL, IMAP_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
            (POP3_SSL_Fetcher.PROTOCOL, POP3_SSL_Fetcher.AVAILABLE_FETCHING_CRITERIA),
            ('EXCHANGE', [])
        ]
)
def test_MailboxModel_getAvailableFetchingCriteria(protocol, expectedFetchingCriteria):
    """Tests :func:`Emailkasten.Models.MailboxModel.MailboxModel.getAvailableFetchingCriteria`."""

    account = baker.make(AccountModel, protocol = protocol)
    mailbox = baker.make(MailboxModel, account = account)
    assert mailbox.getAvailableFetchingCriteria() == expectedFetchingCriteria
