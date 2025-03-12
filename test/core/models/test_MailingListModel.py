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
    :func:`fixture_mailingListModelModel`: Creates an :class:`core.models.MailingListModel.MailingListModel` instance for testing.
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


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks the :class:`core.models.MailingListModel.logger`.

    Returns:
        The email instance for testing.
    """
    return mocker.patch("core.models.MailingListModel.logger", autospec=True)


@pytest.mark.django_db
def test_MailingListModel_default_creation(mailingListModel):
    """Tests the correct default creation of :class:`core.models.MailingListModel.MailingListModel`."""

    assert mailingListModel.list_id is not None
    assert isinstance(mailingListModel.list_id, str)
    assert mailingListModel.list_owner is not None
    assert isinstance(mailingListModel.list_owner, str)
    assert mailingListModel.list_subscribe is not None
    assert isinstance(mailingListModel.list_subscribe, str)
    assert mailingListModel.list_unsubscribe is not None
    assert isinstance(mailingListModel.list_unsubscribe, str)
    assert mailingListModel.list_post is not None
    assert isinstance(mailingListModel.list_post, str)
    assert mailingListModel.list_help is not None
    assert isinstance(mailingListModel.list_help, str)
    assert mailingListModel.list_archive is not None
    assert isinstance(mailingListModel.list_archive, str)
    assert mailingListModel.is_favorite is False
    assert mailingListModel.updated is not None
    assert isinstance(mailingListModel.updated, datetime.datetime)
    assert mailingListModel.created is not None
    assert isinstance(mailingListModel.created, datetime.datetime)

    assert mailingListModel.list_id in str(mailingListModel)


@pytest.mark.django_db
def test_MailingListModel_unique(mailingListModel):
    """Tests the unique constraints of :class:`core.models.MailingListModel.MailingListModel`."""
    with pytest.raises(IntegrityError):
        baker.make(MailingListModel, list_id=mailingListModel.list_id)


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
def test_fromEmailMessage_duplicate(mocker, mailingListModel) -> None:
    emailMessage = EmailMessage()
    mock_getHeader = mocker.patch(
        "core.models.MailingListModel.getHeader",
        autospec=True,
        return_value=mailingListModel.list_id,
    )

    result = MailingListModel.fromEmailMessage(emailMessage)

    assert result == mailingListModel
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
