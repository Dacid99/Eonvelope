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

"""Module with the :class:`UserViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from typing_extensions import override

from api.v1.pagination import Pagination
from api.v1.serializers.user_serializers.UserSerializer import UserSerializer
from Emailkasten.utils import get_config


if TYPE_CHECKING:
    from collections.abc import Sequence

    from django.db.models.query import QuerySet
    from rest_framework.permissions import _SupportsHasPermission


class UserViewSet(viewsets.ModelViewSet):
    """Viewset to manage users."""

    BASENAME = "users"
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    @override
    def get_queryset(self) -> QuerySet[User]:
        """Filters the data for entries accessible the request user.

        Staff and superuser get to access all, others only themselves.

        Returns:
            The user entries matching the request users status.
        """

        if self.request and self.request.user:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return User.objects.all()
            return User.objects.filter(
                username=self.request.user.username
            )
        return User.objects.none()


    def get_permissions(self) -> Sequence[_SupportsHasPermission]:
        """Gets the permission for different request methods.

        Allows POST (registration) for all
        and all other methods only for authenticated and admin users.

        Returns:
            The permission class(es) for the request.
        """
        if self.request.method in ["POST"]:
            if get_config("API_REGISTRATION_ENABLED"):
                return [AllowAny()]
            return [IsAdminUser(), IsAuthenticated()]

        if self.request.method in ["PATCH", "PUT", "DELETE", "GET"]:
            return [IsAuthenticated()]

        return super().get_permissions()
