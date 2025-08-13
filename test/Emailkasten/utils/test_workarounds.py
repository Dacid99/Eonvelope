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

"""Test file for the :mod:`Emailkasten.utils` module."""

import os

import pytest
from django.views import View

from Emailkasten.utils.workarounds import get_config


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the modules logger instance."""
    return mocker.patch("Emailkasten.utils.workarounds.logger", autospec=True)


@pytest.fixture
def mock_getattr(mocker):
    """Fixture mocking `getattr` to mock accessing constance values."""
    return mocker.patch("Emailkasten.utils.workarounds.getattr")


def test_get_config_success(monkeypatch, faker, mock_logger, mock_getattr):
    """Tests getting a constance value in case of success."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    fake_config = faker.word()
    mock_getattr.return_value = fake_config

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == fake_config
    mock_logger.debug.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


def test_get_config_workaround_success(monkeypatch, faker, mock_logger, mock_getattr):
    """Tests getting a constance value in case of success via the workaround."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    mock_getattr.side_effect = Exception

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == fake_config_default

    mock_logger.debug.assert_called()
    mock_logger.critical.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()


def test_get_config_workaround_failure(monkeypatch, faker, mock_logger, mock_getattr):
    """Tests getting a constance value in case of failure."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    mock_getattr.side_effect = ValueError("Constance value not found")

    with pytest.raises(KeyError):
        get_config("NO_CONFIG")

    mock_getattr.assert_called_once()
    mock_logger.debug.assert_called()
    mock_logger.critical.assert_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
