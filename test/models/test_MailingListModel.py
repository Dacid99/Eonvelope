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

"""Test module for :mod:`core.models.MailingListModel`.

Fixtures:
    :func:`fixture_mailingListModel`: Creates an :class:`core.models.MailingListModel.MailingListModel` instance for testing.
"""
from __future__ import annotations

import datetime
from email.message import EmailMessage
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.models.CorrespondentModel import CorrespondentModel
from core.models.MailingListModel import MailingListModel

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(name="mock_logger")
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks the :class:`core.models.MailingListModel.logger`.

    Returns:
        The email instance for testing.
    """
    return mocker.patch("core.models.MailingListModel.logger")


@pytest.fixture(name="mailingList")
def fixture_mailingListModel() -> MailingListModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailingList instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.mark.django_db
def test_MailingListModel_creation(mailingList):
    """Tests the correct default creation of :class:`core.models.MailingListModel.MailingListModel`."""

    assert mailingList.list_id is not None
    assert isinstance(mailingList.list_id, str)
    assert mailingList.list_owner is None
    assert mailingList.list_subscribe is None
    assert mailingList.list_unsubscribe is None
    assert mailingList.list_post is None
    assert mailingList.list_help is None
    assert mailingList.list_archive is None
    assert mailingList.is_favorite is False
    assert mailingList.correspondent is not None
    assert isinstance(mailingList.correspondent, CorrespondentModel)
    assert mailingList.updated is not None
    assert isinstance(mailingList.updated, datetime.datetime)
    assert mailingList.created is not None
    assert isinstance(mailingList.created, datetime.datetime)

    assert mailingList.list_id in str(mailingList)


@pytest.mark.django_db
def test_MailingListModel_foreign_key_deletion(mailingList):
    """Tests the on_delete foreign key constraint in :class:`core.models.MailingListModel.MailingListModel`."""

    assert mailingList is not None
    mailingList.correspondent.delete()
    with pytest.raises(MailingListModel.DoesNotExist):
        mailingList.refresh_from_db()


@pytest.mark.django_db
def test_MailingListModel_unique():
    """Tests the unique constraints of :class:`core.models.MailingListModel.MailingListModel`."""

    mailingList_1 = baker.make(MailingListModel, list_id="abc123")
    mailingList_2 = baker.make(MailingListModel, list_id="abc123")
    assert mailingList_1.list_id == mailingList_2.list_id
    assert mailingList_1.correspondent != mailingList_2.correspondent

    correspondent = baker.make(CorrespondentModel)

    mailingList_1 = baker.make(MailingListModel, correspondent=correspondent)
    mailingList_2 = baker.make(MailingListModel, correspondent=correspondent)
    assert mailingList_1.list_id != mailingList_2.list_id
    assert mailingList_1.correspondent == mailingList_2.correspondent

    baker.make(MailingListModel, list_id="abc123", correspondent=correspondent)
    with pytest.raises(IntegrityError):
        baker.make(MailingListModel, list_id="abc123", correspondent=correspondent)


@pytest.mark.django_db
def test_MailingListModel_fromEmailMessage(mocker):
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader", return_value="list header"
    )

    result = MailingListModel.fromEmailMessage(emailMessage, None)

    mock_getHeader.call_count == 7
    mock_getHeader.assert_has_calls(
        [
            mocker.call(emailMessage, "List-Id"),
            mocker.call(emailMessage, "List-Owner"),
            mocker.call(emailMessage, "List-Subscribe"),
            mocker.call(emailMessage, "List-Unsubscribe"),
            mocker.call(emailMessage, "List-Post"),
            mocker.call(emailMessage, "List-Help"),
            mocker.call(emailMessage, "List-Archive"),
        ]
    )
    assert isinstance(result, MailingListModel)
    assert result.list_id == mock_getHeader.return_value
    assert result.list_owner == mock_getHeader.return_value
    assert result.list_post == mock_getHeader.return_value
    assert result.list_help == mock_getHeader.return_value
    assert result.list_archive == mock_getHeader.return_value
    assert result.list_subscribe == mock_getHeader.return_value
    assert result.list_unsubscribe == mock_getHeader.return_value


@pytest.mark.django_db
def test_fromHeader_duplicate(mocker, mailingList):
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader", return_value=mailingList.list_id
    )

    result = MailingListModel.fromEmailMessage(emailMessage, None)

    assert result == mailingList
    mock_getHeader.assert_called_with(emailMessage, "List-Id")


@pytest.mark.django_db
def test_MailingListModel_fromEmailMessage_no_list_id(mocker, mock_logger):
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader", return_value=None
    )

    result = MailingListModel.fromEmailMessage(emailMessage, None)

    mock_getHeader.call_count == 1
    mock_getHeader.assert_called_with(emailMessage, "List-Id")
    assert result is None
    mock_logger.debug.assert_called()
