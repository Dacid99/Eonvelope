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


import pytest

from Emailkasten.utils import get_config


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    return mocker.patch("Emailkasten.utils.logger")


@pytest.fixture(name="mock_getattr", autouse=True)
def fixture_mock_getattr(mocker):
    return mocker.patch(
        "Emailkasten.utils.getattr", return_value="test-value from constance"
    )


@pytest.fixture(name="mock_constance_settings", autouse=True)
def fixture_mock_constance_settings(monkeypatch):
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {"TEST_CONFIG": ("test-value from settings", "A test value", str)},
    )


def test_get_config_success(mock_logger, mock_getattr):
    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == "test-value from constance"
    mock_logger.debug.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


def test_get_config_workaround_success(mock_logger, mock_getattr):
    mock_getattr.side_effect = Exception

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == "test-value from settings"
    mock_logger.info.assert_called()
    mock_logger.critical.assert_not_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()


def test_get_config_workaround_failure(mock_logger, mock_getattr):
    mock_getattr.side_effect = ValueError("Constance value not found")

    with pytest.raises(KeyError):
        get_config("NO_CONFIG")

    mock_getattr.assert_called_once()
    mock_logger.info.assert_called()
    mock_logger.critical.assert_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()
