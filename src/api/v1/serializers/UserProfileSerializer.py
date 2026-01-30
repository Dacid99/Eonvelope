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

"""Module with the :class:`UserProfileSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from rest_framework import serializers

from eonvelope.models import UserProfile

if TYPE_CHECKING:
    from django.db.models import Model


class UserProfileSerializer(serializers.ModelSerializer[UserProfile]):
    """The serializer for :class:`eonvelope.models.UserProfile`."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    """The :attr:`eonvelope.models.UserProfile.user` field is included but hidden."""

    class Meta:
        """Metadata class for the serializer."""

        model: Final[type[Model]] = UserProfile
        """The model to serialize."""

        exclude = ["id"]
        """Include the id field."""

        extra_kwargs = {
            "paperless_api_key": {"write_only": True},
            "immich_api_key": {"write_only": True},
            "nextcloud_password": {"write_only": True},
        }
