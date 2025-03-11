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

from core.models.MailingListModel import MailingListModel


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks the :class:`core.models.MailingListModel.logger`.

    Returns:
        The email instance for testing.
    """
    return mocker.patch("core.models.MailingListModel.logger", autospec=True)


@pytest.fixture(name="mailingList")
def fixture_mailingListModel() -> MailingListModel:
    """Creates an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailingList instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.mark.django_db
def test_MailingListModel_default_creation(mailingList):
    """Tests the correct default creation of :class:`core.models.MailingListModel.MailingListModel`."""

    assert mailingList.list_id is not None
    assert isinstance(mailingList.list_id, str)
    assert mailingList.list_owner is not None
    assert isinstance(mailingList.list_owner, str)
    assert mailingList.list_subscribe is not None
    assert isinstance(mailingList.list_subscribe, str)
    assert mailingList.list_unsubscribe is not None
    assert isinstance(mailingList.list_unsubscribe, str)
    assert mailingList.list_post is not None
    assert isinstance(mailingList.list_post, str)
    assert mailingList.list_help is not None
    assert isinstance(mailingList.list_help, str)
    assert mailingList.list_archive is not None
    assert isinstance(mailingList.list_archive, str)
    assert mailingList.is_favorite is False
    assert mailingList.updated is not None
    assert isinstance(mailingList.updated, datetime.datetime)
    assert mailingList.created is not None
    assert isinstance(mailingList.created, datetime.datetime)

    assert mailingList.list_id in str(mailingList)


@pytest.mark.django_db
def test_MailingListModel_unique(mailingList):
    """Tests the unique constraints of :class:`core.models.MailingListModel.MailingListModel`."""
    with pytest.raises(IntegrityError):
        baker.make(MailingListModel, list_id=mailingList.list_id)


@pytest.mark.django_db
def test_MailingListModel_fromEmailMessage(mocker):
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader",
        autospec=True,
        return_value="list header",
    )

    result = MailingListModel.fromEmailMessage(emailMessage)

    assert mock_getHeader.call_count == 7
    mock_getHeader.assert_has_calls(
        [
            mocker.call(emailMessage, "List-Id"),
            mocker.call(emailMessage, "List-Owner", fallbackCallable=lambda: ""),
            mocker.call(emailMessage, "List-Subscribe", fallbackCallable=lambda: ""),
            mocker.call(emailMessage, "List-Unsubscribe", fallbackCallable=lambda: ""),
            mocker.call(emailMessage, "List-Post", fallbackCallable=lambda: ""),
            mocker.call(emailMessage, "List-Help", fallbackCallable=lambda: ""),
            mocker.call(emailMessage, "List-Archive", fallbackCallable=lambda: ""),
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
def test_fromEmailMessage_duplicate(mocker, mailingList) -> None:
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader",
        autospec=True,
        return_value=mailingList.list_id,
    )

    result = MailingListModel.fromEmailMessage(emailMessage)

    assert result == mailingList
    mock_getHeader.assert_called_once_with(emailMessage, "List-Id")


@pytest.mark.django_db
def test_MailingListModel_fromEmailMessage_no_list_id(mocker, mock_logger):
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader", autospec=True, return_value=None
    )

    result = MailingListModel.fromEmailMessage(emailMessage)

    assert result is None
    mock_getHeader.assert_called_once_with(emailMessage, "List-Id")
    mock_logger.debug.assert_called()
