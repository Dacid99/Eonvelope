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


"""Test module for :mod:`Emailkasten.Models.MailingListModel`."""

import datetime

import pytest
from django.db import IntegrityError

from .ModelFactories.MailingListModelFactory import MailingListModelFactory
from .ModelFactories.CorrespondentModelFactory import CorrespondentModelFactory


@pytest.mark.django_db
def test_MailingListModel_creation():
    """Tests the correct creation of :class:`Emailkasten.Models.MailingListModel.MailingListModel`."""

    mailingList = MailingListModelFactory(list_id="abc123")
    assert mailingList.list_id == "abc123"
    assert mailingList.list_owner is None
    assert mailingList.list_subscribe is None
    assert mailingList.list_unsubscribe is None
    assert mailingList.list_post is None
    assert mailingList.list_help is None
    assert mailingList.list_archive is None
    assert mailingList.is_favorite is False
    assert mailingList.correspondent is not None
    assert isinstance(mailingList.updated, datetime.datetime)
    assert mailingList.updated is not None
    assert isinstance(mailingList.created, datetime.datetime)
    assert mailingList.created is not None
    assert mailingList.list_id in str(mailingList)


@pytest.mark.django_db
def test_MailingListModel_unique():
    """Tests the uniqie constraints of :class:`Emailkasten.Models.MailingListModel.MailingListModel`."""

    mailingList_1 = MailingListModelFactory(list_id="abc123")
    mailingList_2 = MailingListModelFactory(list_id="abc123")
    assert mailingList_1.list_id == mailingList_2.list_id
    assert mailingList_1.correspondent != mailingList_2.correspondent

    correspondent = CorrespondentModelFactory()

    mailingList_1 = MailingListModelFactory(correspondent = correspondent)
    mailingList_2 = MailingListModelFactory(correspondent = correspondent)
    assert mailingList_1.list_id != mailingList_2.list_id
    assert mailingList_1.correspondent == mailingList_2.correspondent

    MailingListModelFactory(list_id="abc123", correspondent = correspondent)
    with pytest.raises(IntegrityError):
        MailingListModelFactory(list_id="abc123", correspondent = correspondent)
