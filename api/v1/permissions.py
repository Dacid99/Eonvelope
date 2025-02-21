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

"""Provides custom permissions classes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from rest_framework.permissions import IsAuthenticated


if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class IsAdminOrSelf(IsAuthenticated):
    """Permission class to allow access of the user himself and the admins."""

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        """Checks the permissions for a request.

        Args:
            request: The request to check.
            view: The view sending the request.
            obj: The object to access.

        Returns:
            True if `request` is sent by a user
            that is either staff or the owner of `obj`,
            else false.
        """
        return bool(request.user and request.user.is_staff) or request.user == obj
