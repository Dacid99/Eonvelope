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


"""Test module for :mod:`Emailkasten.Models.EMailModel`."""

import datetime

import pytest
from django.db import IntegrityError
from model_bakery import baker

from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Models.MailingListModel import MailingListModel


@pytest.mark.django_db
def test_EMailModel_creation():
    """Tests the correct default creation of :class:`Emailkasten.Models.EMailModel.EMailModel`."""

    email = baker.make(EMailModel)
    assert email.message_id is not None
    assert isinstance(email.message_id, str)
    assert email.datetime is not None
    assert isinstance(email.datetime, datetime.datetime)
    assert email.email_subject is not None
    assert isinstance(email.email_subject, str)
    assert email.bodytext is not None
    assert isinstance(email.bodytext, str)
    assert email.inReplyTo is None
    assert email.datasize is not None
    assert isinstance(email.datasize, int)
    assert email.eml_filepath is None
    assert email.prerender_filepath is None
    assert email.is_favorite is False


    assert email.mailinglist is not None
    assert isinstance(email.mailinglist, MailingListModel)
    assert email.account is not None
    assert isinstance(email.account, AccountModel)
    assert email.comments is None
    assert email.keywords is None
    assert email.importance is None
    assert email.priority is None
    assert email.precedence is None
    assert email.received is None
    assert email.user_agent is None
    assert email.auto_submitted is None
    assert email.content_type is None
    assert email.content_language is None
    assert email.content_location is None
    assert email.x_priority is None
    assert email.x_originated_client is None
    assert email.x_spam is None

    assert isinstance(email.updated, datetime.datetime)
    assert email.updated is not None
    assert isinstance(email.created, datetime.datetime)
    assert email.created is not None

    assert email.message_id in str(email)
    assert str(email.datetime) in str(email)
    assert email.email_subject in str(email)
    assert str(email.account) in str(email)


@pytest.mark.django_db
def test_EMailModel_foreign_key_deletion():
    """Tests the on_delete foreign key constraint in :class:`Emailkasten.Models.EMailModel.EMailModel`."""

    account = baker.make(AccountModel)
    email = baker.make(EMailModel, account = account)
    assert email is not None
    account.delete()
    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()

    mailingList = baker.make(MailingListModel)
    email = baker.make(EMailModel, mailingList = mailingList)
    assert email is not None
    mailingList.delete()
    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()


@pytest.mark.django_db
def test_EMailModel_unique():
    """Tests the unique constraints of :class:`Emailkasten.Models.EMailModel.EMailModel`."""

    email_1 = baker.make(EMailModel, message_id="abc123")
    email_2 = baker.make(EMailModel, message_id="abc123")
    assert email_1.message_id == email_2.message_id
    assert email_1.account != email_2.account

    account = baker.make(AccountModel)

    email_1 = baker.make(EMailModel, account = account)
    email_2 = baker.make(EMailModel, account = account)
    assert email_1.message_id != email_2.message_id
    assert email_1.account == email_2.account

    baker.make(EMailModel, message_id="abc123", account = account)
    with pytest.raises(IntegrityError):
        baker.make(EMailModel, message_id="abc123", account = account)
