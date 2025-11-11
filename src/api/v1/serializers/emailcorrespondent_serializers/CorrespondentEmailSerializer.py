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

"""Module with the :class:`CorrespondentEmailSerializer` serializer class."""

from __future__ import annotations

from typing import ClassVar

from api.v1.serializers.email_serializers.BaseEmailSerializer import BaseEmailSerializer

from .BaseEmailCorrespondentSerializer import BaseEmailCorrespondentSerializer


class CorrespondentEmailSerializer(BaseEmailCorrespondentSerializer):
    """The serializer for emails from :class:`core.models.EmailCorrespondent`.

    Used to serialize the emails belonging to a correspondent. Does not include this correspondent.
    """

    email = BaseEmailSerializer(read_only=True)
    """The email is serialized
    by :class:`api.v1.serializers.SimpleEmailSerializer`.
    """

    class Meta(BaseEmailCorrespondentSerializer.Meta):
        """Metadata class for the serializer."""

        fields: ClassVar[list[str]] = ["email", "mention"]
        """Includes only :attr:`core.models.EmailCorrespondent.EmailCorrespondent.email`
        and :attr:`core.models.EmailCorrespondent.EmailCorrespondent.mention`.
        """
