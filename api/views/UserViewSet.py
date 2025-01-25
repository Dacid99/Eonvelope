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
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from Emailkasten.constants import APIConfiguration
from Emailkasten.Pagination import Pagination
from Emailkasten.permissions import IsAdminOrSelf
from Emailkasten.Serializers.UserSerializers.UserSerializer import UserSerializer

if TYPE_CHECKING:
    from typing import Sequence

    from rest_framework.permissions import _SupportsHasPermission


class UserViewSet(viewsets.ModelViewSet):
    """Viewset to manage users."""

    BASENAME = 'users'
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = Pagination

    def get_permissions(self) -> Sequence[_SupportsHasPermission]:
        """Gets the permission for different request methods.
        Allows POST (registration) for all
        and all other methods only for authenticated and admin users.

        Returns:
            The permission class(es) for the request.
        """
        if self.request.method in ['POST']:
            if APIConfiguration.REGISTRATION_ENABLED:
                return [AllowAny()]
            else:
                return [IsAdminUser(), IsAuthenticated()]

        elif self.request.method in ['PATCH','PUT','DELETE','GET']:
            return [IsAdminOrSelf(), IsAuthenticated()]

        return super().get_permissions()
