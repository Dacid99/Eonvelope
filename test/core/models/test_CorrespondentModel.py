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
    :func:`fixture_correspondentModel`: Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.
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


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker) -> MagicMock:
    """Mocks the :attr:`core.models.CorrespondentModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.CorrespondentModel.logger", autospec=True)


@pytest.fixture(name="correspondent")
def fixture_correspondentModel() -> CorrespondentModel:
    """Creates an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.

    Returns:
        The email instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.mark.django_db
def test_CorrespondentModel_default_creation(correspondent):
    """Tests the correct default creation of :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    assert correspondent.email_name is not None
    assert isinstance(correspondent.email_name, str)
    assert correspondent.email_address is not None
    assert isinstance(correspondent.email_address, str)
    assert correspondent.is_favorite is False
    assert correspondent.updated is not None
    assert isinstance(correspondent.updated, datetime.datetime)
    assert correspondent.created is not None
    assert isinstance(correspondent.created, datetime.datetime)

    assert correspondent.email_address in str(correspondent)


@pytest.mark.django_db
def test_CorrespondentModel_unique(correspondent):
    """Tests the unique constraint in :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    with pytest.raises(IntegrityError):
        baker.make(
            CorrespondentModel,
            email_name=correspondent.email_name,
            email_address=correspondent.email_address,
        )


@pytest.mark.django_db
def test_fromHeader_success(mocker, faker):
    mock_parseCorrespondentHeader = mocker.patch(
        "core.models.CorrespondentModel.parseCorrespondentHeader",
        autospec=True,
        return_value=(faker.name(), faker.email()),
    )

    result = CorrespondentModel.fromHeader("correspondent header")

    assert isinstance(result, CorrespondentModel)
    mock_parseCorrespondentHeader.assert_called_once_with("correspondent header")
    assert result.email_name == mock_parseCorrespondentHeader.return_value[0]
    assert result.email_address == mock_parseCorrespondentHeader.return_value[1]


@pytest.mark.django_db
def test_fromHeader_duplicate(mocker, faker, correspondent):
    mock_parseCorrespondentHeader = mocker.patch(
        "core.models.CorrespondentModel.parseCorrespondentHeader",
        autospec=True,
        return_value=(faker.name(), correspondent.email_address),
    )

    result = CorrespondentModel.fromHeader("correspondent header")

    assert result == correspondent
    mock_parseCorrespondentHeader.assert_called_once_with("correspondent header")


@pytest.mark.django_db
def test_fromHeader_no_address(mocker, faker, mock_logger):
    mock_parseCorrespondentHeader = mocker.patch(
        "core.models.CorrespondentModel.parseCorrespondentHeader",
        autospec=True,
        return_value=(faker.name(), ""),
    )

    result = CorrespondentModel.fromHeader("correspondent header")

    assert result is None
    mock_parseCorrespondentHeader.assert_called_once_with("correspondent header")
    mock_logger.debug.assert_called()
