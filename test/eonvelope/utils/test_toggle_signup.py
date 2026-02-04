# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Test file for the :mod:`eonvelope.utils` module."""

import pytest
from django.views import View

from eonvelope.utils.toggle_signup import (
    ToggleSignupAccountAdapter,
    ToggleSignUpPermissionClass,
)


@pytest.fixture
def mock_request(mocker):
    """An empty mock :class:`rest_framework.request.Request`."""
    return mocker.patch("rest_framework.request.Request", autospec=True)


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "ENV_REGISTRATION_ENABLED",
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True, True),
        (True, False, True, True),
        (False, True, True, False),
        (False, False, True, False),
        (True, True, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
def test_ToggleSignUpAdapter_is_open_for_signup(
    settings,
    override_config,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = ENV_REGISTRATION_ENABLED
    settings.REGISTRATION_ENABLED_DEFAULT = REGISTRATION_ENABLED_DEFAULT

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignupAccountAdapter().is_open_for_signup(mock_request)

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True),
        (True, False, False),
        (False, True, False),
        (False, False, False),
    ],
)
def test_ToggleSignUpAdapter_is_open_for_signup_fallback(
    settings,
    override_config,
    mock_request,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is not set."""
    settings.REGISTRATION_ENABLED = REGISTRATION_ENABLED_DEFAULT

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignupAccountAdapter().is_open_for_signup(mock_request)

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "ENV_REGISTRATION_ENABLED",
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True, True),
        (True, False, True, True),
        (False, True, True, False),
        (False, False, True, False),
        (True, True, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission__noauth(
    settings,
    override_config,
    django_user_model,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = ENV_REGISTRATION_ENABLED
    settings.REGISTRATION_ENABLED_DEFAULT = REGISTRATION_ENABLED_DEFAULT

    mock_request.user = django_user_model()

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "ENV_REGISTRATION_ENABLED",
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True, True),
        (True, False, True, True),
        (False, True, True, False),
        (False, False, True, False),
        (True, True, False, False),
        (True, False, False, False),
        (False, True, False, False),
        (False, False, False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission__auth_user(
    settings,
    override_config,
    owner_user,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = ENV_REGISTRATION_ENABLED
    settings.REGISTRATION_ENABLED_DEFAULT = REGISTRATION_ENABLED_DEFAULT
    mock_request.user = owner_user
    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "ENV_REGISTRATION_ENABLED",
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True, True),
        (True, False, True, True),
        (False, True, True, True),
        (False, False, True, True),
        (True, True, False, True),
        (True, False, False, True),
        (False, True, False, True),
        (False, False, False, True),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission__auth_admin(
    settings,
    override_config,
    admin_user,
    mock_request,
    ENV_REGISTRATION_ENABLED,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = ENV_REGISTRATION_ENABLED
    settings.REGISTRATION_ENABLED_DEFAULT = REGISTRATION_ENABLED_DEFAULT
    mock_request.user = admin_user

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (False, False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback__noauth(
    settings,
    override_config,
    django_user_model,
    mock_request,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = REGISTRATION_ENABLED_DEFAULT
    mock_request.user = django_user_model()

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (False, False, False),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback__auth_user(
    settings,
    override_config,
    owner_user,
    mock_request,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = REGISTRATION_ENABLED_DEFAULT
    mock_request.user = owner_user
    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "REGISTRATION_ENABLED_DEFAULT",
        "CONSTANCE_REGISTRATION_ENABLED",
        "expected_result",
    ),
    [
        (True, True, True),
        (False, True, True),
        (True, False, True),
        (False, False, True),
    ],
)
def test_ToggleSignUpPermissionClass_has_permission_fallback__auth_admin(
    settings,
    override_config,
    admin_user,
    mock_request,
    REGISTRATION_ENABLED_DEFAULT,
    CONSTANCE_REGISTRATION_ENABLED,
    expected_result,
):
    """Tests the ToggleSignUpAdapter in case "REGISTRATION_ENABLED" environment is set."""
    settings.REGISTRATION_ENABLED = REGISTRATION_ENABLED_DEFAULT
    mock_request.user = admin_user

    with override_config(REGISTRATION_ENABLED=CONSTANCE_REGISTRATION_ENABLED):
        result = ToggleSignUpPermissionClass().has_permission(mock_request, View())

    assert result is expected_result
