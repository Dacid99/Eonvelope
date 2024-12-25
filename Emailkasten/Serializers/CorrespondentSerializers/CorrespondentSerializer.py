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

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from ...Models.CorrespondentModel import CorrespondentModel
from ...Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ..EMailCorrespondentsSerializers.CorrespondentEMailSerializer import \
    CorrespondentEMailSerializer
from ..MailingListSerializers.SimpleMailingListSerializer import \
    SimpleMailingListSerializer


class CorrespondentSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.CorrespondentModel`.
    Uses all fields including all emails and mailinglists mentioning the correspondent.
    Use exclusively in a :restframework::class:`viewsets.ReadOnlyModelViewSet`."""

    emails = serializers.SerializerMethodField()
    """The emails are set from the :class:`Emailkasten.Models.EMailCorrespondentsModel` via :func:`get_emails`."""

    mailinglist = SimpleMailingListSerializer(many=True, read_only=True)
    """The mailinglists are serialized by :class:`Emailkasten.MailingListSerializers.MailingListSerializer`."""


    class Meta:
        """Metadata class for the serializer."""

        model = CorrespondentModel

        fields = '__all__'
        """Include all fields."""


    def get_emails(self, object: CorrespondentModel) -> ReturnDict|None:
        """Serializes the emails connected to the instance to be serialized.

        Args:
            object: The instance being serialized.

        Returns:
            The serialized emails connected to the instance to be serialized.
            None if the the user is not authenticated.
        """
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            correspondentemails = EMailCorrespondentsModel.objects.filter(correspondent=object, email__account__user=user).distinct()
            return CorrespondentEMailSerializer(correspondentemails, many=True, read_only=True).data
        else:
            return None
