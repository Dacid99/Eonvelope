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

"""Module with the :class:`CorrespondentEMailSerializer` serializer class."""

from __future__ import annotations

from typing import ClassVar

from ..email_serializers.BaseEMailSerializer import BaseEMailSerializer
from .BaseEMailCorrespondentSerializer import BaseEMailCorrespondentSerializer


class CorrespondentEMailSerializer(BaseEMailCorrespondentSerializer):
    """The serializer for emails from :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`.

    Used to serialize the emails belonging to a correspondent. Does not include this correpondent.
    """

    email = BaseEMailSerializer(read_only=True)
    """The email is serialized
    by :class:`api.v1.serializers.EMailSerializers.SimpleEMailSerializer.SimpleEMailSerializer`.
    """

    class Meta(BaseEMailCorrespondentSerializer.Meta):
        """Metadata class for the serializer."""

        fields: ClassVar[list[str]] = ["email", "mention"]
        """Includes only :attr:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.email`
        and :attr:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.mention`.
        """
