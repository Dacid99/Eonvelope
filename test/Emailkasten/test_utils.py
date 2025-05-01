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

from Emailkasten.utils import (
    ToggleSignupAccountAdapter,
    ToggleSignUpPermissionClass,
    get_config,
)


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the modules logger instance."""
    return mocker.patch("Emailkasten.utils.logger", autospec=True)


@pytest.fixture
def mock_getattr(mocker):
    """Fixture mocking `getattr` to mock accessing constance values."""
    return mocker.patch("Emailkasten.utils.getattr")


@pytest.fixture
def mock_httpRequest(mocker):
    return mocker.patch("django.http.HttpRequest", autospec=True)


@pytest.fixture
def mock_request(mocker):
    return mocker.patch("rest_framework.request.Request", autospec=True)


@pytest.mark.parametrize(
    "ENV_REGISTRATION_ENABLED, DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", "1", True, True),
        ("1", "0", True, True),
        ("0", "1", True, False),
        ("0", "0", True, False),
        ("1", "1", False, False),
        ("1", "0", False, False),
        ("0", "1", False, False),
        ("0", "0", False, False),
    ],
)
def test_ToggleSignUpAdapter_is_open_for_signup(
    monkeypatch,
    mock_httpRequest,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {
            "REGISTRATION_ENABLED": (
                CONSTANCE_REGISTRATION_ENABLED,
                "The patched REGISTRATION_ENABLED setting",
                bool,
            )
        },
    )

    result = ToggleSignupAccountAdapter().is_open_for_signup(mock_httpRequest)

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.parametrize(
    "DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", True, True),
        ("1", False, False),
        ("0", True, False),
        ("0", False, False),
    ],
)
def test_ToggleSignUpAdapter_is_open_for_signup_fallback(
    monkeypatch,
    mock_request,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is not set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {
            "REGISTRATION_ENABLED": (
                CONSTANCE_REGISTRATION_ENABLED,
                "The patched REGISTRATION_ENABLED setting",
                bool,
            )
        },
    )

    result = ToggleSignupAccountAdapter().is_open_for_signup(mock_request)

    assert result is expected_result


@pytest.mark.parametrize(
    "ENV_REGISTRATION_ENABLED, DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", "1", True, True),
        ("1", "0", True, True),
        ("0", "1", True, False),
        ("0", "0", True, False),
        ("1", "1", False, False),
        ("1", "0", False, False),
        ("0", "1", False, False),
        ("0", "0", False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_noauth(
    monkeypatch,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {
            "REGISTRATION_ENABLED": (
                CONSTANCE_REGISTRATION_ENABLED,
                "The patched REGISTRATION_ENABLED setting",
                bool,
            )
        },
    )
    mock_request.user.is_authenticated = False
    mock_request.user.is_staff = False

    result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.parametrize(
    "ENV_REGISTRATION_ENABLED, DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", "1", True, True),
        ("1", "0", True, True),
        ("0", "1", True, False),
        ("0", "0", True, False),
        ("1", "1", False, False),
        ("1", "0", False, False),
        ("0", "1", False, False),
        ("0", "0", False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_auth_user(
    monkeypatch,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {
            "REGISTRATION_ENABLED": (
                CONSTANCE_REGISTRATION_ENABLED,
                "The patched REGISTRATION_ENABLED setting",
                bool,
            )
        },
    )
    mock_request.user.is_authenticated = True
    mock_request.user.is_staff = False

    result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.parametrize(
    "ENV_REGISTRATION_ENABLED, DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", "1", True, True),
        ("1", "0", True, True),
        ("0", "1", True, True),
        ("0", "0", True, True),
        ("1", "1", False, True),
        ("1", "0", False, True),
        ("0", "1", False, True),
        ("0", "0", False, True),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_auth_admin(
    monkeypatch,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.DEFAULT_REGISTRATION_ENABLED", DEFAULT_REGISTRATION_ENABLED
    )
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {
            "REGISTRATION_ENABLED": (
                CONSTANCE_REGISTRATION_ENABLED,
                "The patched REGISTRATION_ENABLED setting",
                bool,
            )
        },
    )
    mock_request.user.is_authenticated = True
    mock_request.user.is_staff = True

    result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


def test_get_config_success(monkeypatch, faker, mock_logger, mock_getattr):
    """Tests getting a constance value in case of success."""
    fake_config = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config, "A test value", str)},
    )
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
    fake_config = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config, "A test value", str)},
    )
    mock_getattr.side_effect = Exception

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == fake_config

    mock_logger.info.assert_called()
    mock_logger.critical.assert_not_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()


def test_get_config_workaround_failure(monkeypatch, faker, mock_logger, mock_getattr):
    """Tests getting a constance value in case of failure."""
    fake_config = faker.word()
    monkeypatch.setattr(
        "Emailkasten.utils.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config, "A test value", str)},
    )
    mock_getattr.side_effect = ValueError("Constance value not found")

    with pytest.raises(KeyError):
        get_config("NO_CONFIG")

    mock_getattr.assert_called_once()
    mock_logger.info.assert_called()
    mock_logger.critical.assert_called()
    mock_logger.debug.assert_not_called()
    mock_logger.error.assert_not_called()
