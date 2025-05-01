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

from Emailkasten.utils.toggle_signup import (
    ToggleSignupAccountAdapter,
    ToggleSignUpPermissionClass,
)


@pytest.fixture
def mock_request(mocker):
    return mocker.patch("rest_framework.request.Request", autospec=True)


@pytest.mark.django_db
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
    override_config,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignupAccountAdapter().is_open_for_signup(mock_request)

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.django_db
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
    override_config,
    mock_request,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is not set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignupAccountAdapter().is_open_for_signup(mock_request)

    assert result is expected_result


@pytest.mark.django_db
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
    override_config,
    django_user_model,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = django_user_model()

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.django_db
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
    override_config,
    owner_user,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = owner_user
    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.django_db
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
    override_config,
    admin_user,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ["REGISTRATION_ENABLED"] = ENV_REGISTRATION_ENABLED
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = admin_user

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result

    os.environ.pop("REGISTRATION_ENABLED", None)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", True, True),
        ("0", True, False),
        ("1", False, False),
        ("0", False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback_noauth(
    monkeypatch,
    override_config,
    django_user_model,
    mock_request,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = django_user_model()

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", True, True),
        ("0", True, False),
        ("1", False, False),
        ("0", False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback_auth_user(
    monkeypatch,
    override_config,
    owner_user,
    mock_request,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = owner_user
    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    "DEFAULT_REGISTRATION_ENABLED, CONSTANCE_REGISTRATION_ENABLED, expected_result",
    [
        ("1", True, True),
        ("0", True, True),
        ("1", False, True),
        ("0", False, True),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback_auth_admin(
    monkeypatch,
    override_config,
    admin_user,
    mock_request,
    DEFAULT_REGISTRATION_ENABLED,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    os.environ.pop("REGISTRATION_ENABLED", None)
    monkeypatch.setattr(
        "Emailkasten.utils.toggle_signup.DEFAULT_REGISTRATION_ENABLED",
        DEFAULT_REGISTRATION_ENABLED,
    )
    mock_request.user = admin_user

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result
