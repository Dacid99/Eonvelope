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


"""Test module for :mod:`core.models.CorrespondentModel`.

Fixtures:
    :func:`fixture_correspondentModelModel`: Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.models.CorrespondentModel import CorrespondentModel


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks the :attr:`core.models.CorrespondentModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.CorrespondentModel.logger", autospec=True)


@pytest.fixture
def mock_parseCorrespondentHeader(mocker, faker):
    """Fixture mocking :func:`core.models.CorrespondentModel.parseCorrespondentHeader`."""
    return mocker.patch(
        "core.models.CorrespondentModel.parseCorrespondentHeader",
        autospec=True,
        return_value=(faker.name(), faker.email()),
    )


@pytest.mark.django_db
def test_CorrespondentModel_fields(correspondentModel):
    """Tests the fields of :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    assert correspondentModel.email_name is not None
    assert isinstance(correspondentModel.email_name, str)
    assert correspondentModel.email_address is not None
    assert isinstance(correspondentModel.email_address, str)
    assert correspondentModel.is_favorite is False
    assert correspondentModel.updated is not None
    assert isinstance(correspondentModel.updated, datetime.datetime)
    assert correspondentModel.created is not None
    assert isinstance(correspondentModel.created, datetime.datetime)


@pytest.mark.django_db
def test_CorrespondentModel___str__(correspondentModel):
    """Tests the string representation of :class:`core.models.CorrespondentModel.CorrespondentModel`."""
    assert correspondentModel.email_address in str(correspondentModel)


@pytest.mark.django_db
def test_CorrespondentModel_unique_constraints(correspondentModel):
    """Tests the unique constraint in :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    with pytest.raises(IntegrityError):
        baker.make(
            CorrespondentModel,
            email_name=correspondentModel.email_name,
            email_address=correspondentModel.email_address,
        )


@pytest.mark.django_db
def test_CorrespondentModel_fromHeader_success(mock_parseCorrespondentHeader):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.fromHeader`
    in case of success.
    """
    result = CorrespondentModel.fromHeader("correspondentModel header")

    assert isinstance(result, CorrespondentModel)
    mock_parseCorrespondentHeader.assert_called_once_with("correspondentModel header")
    assert result.email_name == mock_parseCorrespondentHeader.return_value[0]
    assert result.email_address == mock_parseCorrespondentHeader.return_value[1]


@pytest.mark.django_db
def test_CorrespondentModel_fromHeader_duplicate(
    correspondentModel, mock_parseCorrespondentHeader
):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.fromHeader`
    in case the correspondent to be prepared is already being in the database.
    """
    mock_parseCorrespondentHeader.return_value = (
        mock_parseCorrespondentHeader.return_value[0],
        correspondentModel.email_address,
    )

    result = CorrespondentModel.fromHeader("correspondentModel header")

    assert result == correspondentModel
    mock_parseCorrespondentHeader.assert_called_once_with("correspondentModel header")


@pytest.mark.django_db
def test_CorrespondentModel_fromHeader_no_address(
    mock_logger, mock_parseCorrespondentHeader
):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.fromHeader`
    in case of there is no address in the header.
    """
    mock_parseCorrespondentHeader.return_value = (
        mock_parseCorrespondentHeader.return_value[0],
        "",
    )

    result = CorrespondentModel.fromHeader("correspondentModel header")

    assert result is None
    mock_parseCorrespondentHeader.assert_called_once_with("correspondentModel header")
    mock_logger.debug.assert_called()
