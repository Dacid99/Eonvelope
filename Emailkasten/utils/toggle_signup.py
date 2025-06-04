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

"""Module with utility for the :mod:`Emailkasten` project ."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from ..utils.workarounds import get_config


if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class ToggleSignupAccountAdapter(
    DefaultAccountAdapter
):  # pylint: disable=abstract-method  # phone methods are (currently) not used
    """AccountAdapter class to allow toggling of signups for django-allauth."""

    @override
    def is_open_for_signup(self, request: Request) -> bool:  # type: ignore[misc]  # Mypy can't find the base method for this
        """Checks whether signups are allowed.

        Args:
            request: The signup request.

        Returns:
            Whether signups are allowed.
        """
        return bool(settings.REGISTRATION_ENABLED) and bool(
            get_config("REGISTRATION_ENABLED")
        )


class ToggleSignUpPermissionClass(AllowAny, IsAuthenticated, IsAdminUser):
    """Permission class to allow toggling of signups for dj-rest-auth."""

    @override
    def has_permission(self, request: Request, view: APIView) -> bool:
        """Checks a signup request is permitted.

        If registration is disabled only staff members can make signup requests.

        Args:
            request: The signup request.

        Returns:
            If the signup request is permitted.
        """
        if bool(settings.REGISTRATION_ENABLED) and bool(
            get_config("REGISTRATION_ENABLED")
        ):
            return AllowAny.has_permission(self, request, view)
        return IsAdminUser.has_permission(self, request, view)
