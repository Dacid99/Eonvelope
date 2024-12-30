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


"""Test module for :mod:`Emailkasten.Models.MailboxModel`.

Fixtures:
    :func:`fixture_mailboxModel`: Creates an :class:`Emailkasten.Models.MailboxModel.MailboxModel` instance for testing.
"""

import datetime

import pytest
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten import constants
from Emailkasten.Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from Emailkasten.Fetchers.IMAPFetcher import IMAPFetcher
from Emailkasten.Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from Emailkasten.Fetchers.POP3Fetcher import POP3Fetcher
from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.MailboxModel import MailboxModel


@pytest.fixture(name='mailbox')
def fixture_mailboxModel() -> MailboxModel:
    """Creates an :class:`Emailkasten.Models.MailboxModel.MailboxModel`.

    Returns:
        The mailbox instance for testing.
    """
    return baker.make(MailboxModel)


@pytest.mark.django_db
def test_MailboxModel_creation(mailbox):
    """Tests the correct default creation of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    assert mailbox.name is not None
    assert mailbox.account is not None
    assert isinstance(mailbox.account, AccountModel)
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
def test_MailboxModel_foreign_key_deletion(mailbox):
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    assert mailbox is not None
    mailbox.account.delete()
    with pytest.raises(MailboxModel.DoesNotExist):
        mailbox.refresh_from_db()


@pytest.mark.django_db
def test_MailboxModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.MailboxModel.MailboxModel`."""

    mailingList_1 = baker.make(MailboxModel, name="abc123")
    mailingList_2 = baker.make(MailboxModel, name="abc123")
    assert mailingList_1.name == mailingList_2.name
    assert mailingList_1.account != mailingList_2.account

    account = baker.make(AccountModel)

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
def test_MailboxModel_getAvailableFetchingCriteria(mailbox, protocol: str, expectedFetchingCriteria: list[str]):
    """Tests :func:`Emailkasten.Models.MailboxModel.MailboxModel.getAvailableFetchingCriteria`.

    Args:
        protocol: The protocol parameter.
        expectedFetchingCriteria: The expected fetchingCriteria result parameter.
    """

    mailbox.account.protocol = protocol
    mailbox.account.save()
    assert mailbox.getAvailableFetchingCriteria() == expectedFetchingCriteria
