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
from django.http import HttpRequest

from Emailkasten.utils import ToggleSignupAccountAdapter, get_config


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the modules logger instance."""
    return mocker.patch("Emailkasten.utils.logger", autospec=True)


@pytest.fixture(autouse=True)
def mock_getattr(mocker):
    """Fixture mocking `getattr` to mock accessing constance values."""
    return mocker.patch(
        "Emailkasten.utils.getattr", return_value="test-value from constance"
    )


@pytest.fixture
def mock_constance_settings(monkeypatch):
    """Fixture replacing the constance settings."""
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {"TEST_CONFIG": ("test-value from settings", "A test value", str)},
    )


@pytest.mark.parametrize(
    "REGISTRATION_ENABLED, DEFAULT_REGISTRATION_ENABLED, expected_result",
    [
        ("1", "1", True),
        ("0", "0", False),
        ("1", "0", True),
        ("0", "1", False),
    ],
)
def test_ToggleSignUpAdapter_is_open_for_signup(
    monkeypatch,
    REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )

    result = ToggleSignupAccountAdapter().is_open_for_signup(HttpRequest())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.parametrize(
    "DEFAULT_REGISTRATION_ENABLED, expected_result",
    [("1", True), ("0", False)],
)
def test_ToggleSignUpAdapter_is_open_for_signup_fallback(
    monkeypatch, DEFAULT_REGISTRATION_ENABLED, expected_result
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is not set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )

    result = ToggleSignupAccountAdapter().is_open_for_signup(HttpRequest())

    assert result is expected_result


def test_get_config_success(mock_logger, mock_getattr, mock_constance_settings):
    """Tests getting a constance value in case of success."""
    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == "test-value from constance"
    mock_logger.debug.assert_not_called()
    mock_logger.info.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


def test_get_config_workaround_success(
    mock_logger, mock_getattr, mock_constance_settings
):
    """Tests getting a constance value in case of success via the workaround."""
    mock_getattr.side_effect = Exception

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == "test-value from settings"
    mock_logger.info.assert_called()
    mock_logger.critical.assert_not_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()


def test_get_config_workaround_failure(
    mock_logger, mock_getattr, mock_constance_settings
):
    """Tests getting a constance value in case of failure."""
    mock_getattr.side_effect = ValueError("Constance value not found")

    with pytest.raises(KeyError):
        get_config("NO_CONFIG")

    mock_getattr.assert_called_once()
    mock_logger.info.assert_called()
    mock_logger.critical.assert_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()
