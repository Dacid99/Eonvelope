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

"""Module with additional authentication methods for Eonvelope API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from allauth.mfa.adapter import get_adapter
from django.utils.translation import gettext_lazy as _
from drf_spectacular.authentication import BasicScheme
from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication

if TYPE_CHECKING:
    from django_stubs_ext import StrOrPromise
    from drf_spectacular.openapi import AutoSchema
    from rest_framework.request import Request


class BasicNoMFAuthentication(BasicAuthentication):
    """Extended Basic authentication to account for MFA.

    References:
        https://github.com/paperless-ngx/paperless-ngx/blob/dev/src/paperless/auth.py#L77
    """

    @override
    def authenticate(self, request: Request) -> tuple[Any, Any] | None:
        """Extended to check whether MFA is enabled for the authenticating user."""
        user_tuple = super().authenticate(request)
        user = user_tuple[0] if user_tuple else None
        mfa_adapter = get_adapter()
        if user and mfa_adapter.is_mfa_enabled(user):
            raise exceptions.AuthenticationFailed("MFA required")
        return user_tuple


class BasicNoMFScheme(BasicScheme):
    """Extended Basic auth scheme to account for MFA."""

    target_class = "api.auth.BasicNoMFAuthentication"

    @override
    def get_security_definition(
        self, auto_schema: AutoSchema
    ) -> dict[str, StrOrPromise]:
        security_definition = super().get_security_definition(auto_schema)
        security_definition["description"] = _(
            "Basic authentication is only allowed if you do not have MFA enabled."
        )
        return security_definition
