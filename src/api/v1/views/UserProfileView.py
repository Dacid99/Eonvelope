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

"""Module with the :class:`UserProfileViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers import UserProfileSerializer

if TYPE_CHECKING:
    from eonvelope.models import UserProfile


@extend_schema_view(
    retrieve=extend_schema(description=_("Retrieves the user's profile data.")),
    update=extend_schema(description=_("Updates the user's profile data.")),
)
class UserProfileView(RetrieveUpdateAPIView):
    """View for retrieving and updating the users :class:`eonvelope.models.UserProfile`."""

    NAME = "profile"
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    @override
    def get_object(self) -> UserProfile:
        """Fetches the profile connected to the request user.

        Returns:
            The UserProfile model of the request user.
        """
        return self.request.user.profile  # type: ignore[union-attr]  # user auth is checked by permissions, we also test for this
