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

"""Module with the :class:`EMailCorrespondentsSerializer` serializer class."""

from ..CorrespondentSerializers.BaseCorrespondentSerializer import \
    BaseCorrespondentSerializer
from .BaseEMailCorrespondentSerializer import BaseEMailCorrespondentSerializer


class EMailCorrespondentSerializer(BaseEMailCorrespondentSerializer):
    """The serializer for correspondents from :class:`Emailkasten.Models.EMailCorrespondentsModel`.
    Used to serialize the correspondent belonging to an email. Does not include that email.
    """

    correspondent = BaseCorrespondentSerializer(read_only=True)
    """The correspondent is serialized
    by :class:`Emailkasten.Serializers.CorrespondentSerializers.SimpleCorrespondentSerializer.SimpleCorrespondentSerializer`.
    """

    class Meta(BaseEMailCorrespondentSerializer.Meta):
        """Metadata class for the serializer."""

        fields = ['correspondent', 'mention']
        """Includes only
        :attr:`Emailkasten.Models.EMailCorrespondentsModel.EMailCorrespondentsModel.correspondent`
        and :attr:`Emailkasten.Models.EMailCorrespondentsModel.EMailCorrespondentsModel.mention`.
        """
