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

from core.models.CorrespondentModel import CorrespondentModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ..emailcorrespondents_serializers.CorrespondentEMailSerializer import \
    CorrespondentEMailSerializer
from ..mailinglist_serializers.SimpleMailingListSerializer import \
    SimpleMailingListSerializer
from .BaseCorrespondentSerializer import BaseCorrespondentSerializer


class CorrespondentSerializer(BaseCorrespondentSerializer):
    """The standard serializer for a :class:`core.models.CorrespondentModel`.
    Includes a nested serializer for
    the :attr:`core.models.CorrespondentModel.CorrespondentModel.emails`
    and :attr:`core.models.CorrespondentModel.CorrespondentModel.mailinglist` fields.
    """

    emails = serializers.SerializerMethodField(read_only=True)
    """The emails are set from the
    :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`
    via :func:`get_emails`.
    """

    mailinglist = SimpleMailingListSerializer(many=True, read_only=True)
    """The mailinglists are serialized
    by :class:`Emailkasten.MailingListSerializers.SimpleMailingListSerializer.SimpleMailingListSerializer`.
    """

    class Meta(BaseCorrespondentSerializer.Meta):
        """Metadata class for the serializer."""


    def get_emails(self, object: CorrespondentModel) -> ReturnDict|None:
        """Serializes the emails connected to the instance to be serialized.

        Args:
            object: The instance being serialized.

        Returns:
            The serialized emails connected to the instance to be serialized.
            An empty list if the the user is not authenticated.
        """
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            correspondentemails = EMailCorrespondentsModel.objects.filter(correspondent=object, email__account__user=user).distinct()
            return CorrespondentEMailSerializer(correspondentemails, many=True, read_only=True).data
        else:
            return []
