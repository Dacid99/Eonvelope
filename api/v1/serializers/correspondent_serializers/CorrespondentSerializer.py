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

"""Module with the :class:`CorrespondentSerializer` serializer class."""

# ruff: noqa: TC001 TC002
# TYPE_CHECKING guard doesn't work with drf-spectacular: https://github.com/tfranzel/drf-spectacular/issues/390

from __future__ import annotations

from typing import Any

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Correspondent

from ..emailcorrespondent_serializers import (
    CorrespondentEmailSerializer,
)
from .BaseCorrespondentSerializer import BaseCorrespondentSerializer


class CorrespondentSerializer(BaseCorrespondentSerializer):
    """The standard serializer for a :class:`core.models.Correspondent.Correspondent`.
    `core.models.Correspondent`
        Includes a nested serializer for
        the :attr:`core.models.Correspondent.Correspondent.emails` fields.
    """

    emails = serializers.SerializerMethodField(read_only=True)
    """The emails are set from the
    :class:`core.models.EmailCorrespondent.EmailCorrespondent`
    via :fu`core.models.EmailCorrespondent`
    """

    def get_emails(self, instance: Correspondent) -> ReturnDict[str, Any]:
        """Serializes the emails connected to the instance to be serialized.

        Args:
            instance: The instance being serialized.

        Returns:
            The serialized emails connected to the instance to be serialized.
            An empty list if the the user is not authenticated.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None:
            correspondentemails = instance.correspondentemails.filter(
                email__mailbox__account__user=user
            ).distinct()
        else:
            correspondentemails = instance.correspondentemails.none()
        return CorrespondentEmailSerializer(
            correspondentemails, many=True, read_only=True
        ).data
