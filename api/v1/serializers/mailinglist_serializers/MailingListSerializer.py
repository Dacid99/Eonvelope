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

"""Module with the :class:`MailingListSerializer` serializer class."""

# ruff: noqa: TC001 TC002
# TYPE_CHECKING guard doesnt work with drf-spectacular: https://github.com/tfranzel/drf-spectacular/issues/390

from __future__ import annotations

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from core.constants import HeaderFields
from core.models.CorrespondentModel import CorrespondentModel
from core.models.MailingListModel import MailingListModel

from ..correspondent_serializers.BaseCorrespondentSerializer import (
    BaseCorrespondentSerializer,
)
from ..email_serializers.BaseEMailSerializer import BaseEMailSerializer
from .BaseMailingListSerializer import BaseMailingListSerializer


class MailingListSerializer(BaseMailingListSerializer):
    """The standard serializer for a :class:`core.models.MailingList`.

    Includes nested serializers for the :attr:`core.models.MailingList.MailingList.emails`,
    :attr:`core.models.MailingList.MailingList.correspondent` foreign key fields
    as well as a method field for the count of elements in :attr:`core.models.MailingList.MailingList.emails`.
    """

    emails = serializers.SerializerMethodField(read_only=True)
    """The emails from the mailinglist are serialized
    by :class:`api.v1.serializers.EMailSerializers.BaseEMailSerializer.BaseEMailSerializer`.
    """

    from_correspondents = serializers.SerializerMethodField(read_only=True)
    """The correspondent sending the mailinglist are serialized
    by :class:`api.v1.serializers.CorrespondentSerializers.BaseCorrespondentSerializer.BaseCorrespondentSerializer`.
    """

    def get_emails(self, instance: MailingListModel) -> ReturnDict | list:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            instance: The instance being serialized.

        Returns:
            The serialized From correspondents connected to the instance to be serialized.
            An empty list if the the user is not authenticated.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None:
            emails = instance.emails.filter(mailbox__account__user=user)
            return BaseEMailSerializer(emails, many=True, read_only=True).data
        return []

    def get_from_correspondents(self, instance: MailingListModel) -> ReturnDict | list:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            instance: The instance being serialized.

        Returns:
            The serialized From correspondents connected to the instance to be serialized.
            An empty list if the the user is not authenticated.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is not None:
            from_correspondents = CorrespondentModel.objects.filter(
                emails__mailinglist=instance,
                correspondentemails__mention=HeaderFields.Correspondents.FROM,
                emails__mailbox__account__user=user,
            ).distinct()
            return BaseCorrespondentSerializer(
                from_correspondents, many=True, read_only=True
            ).data
        return []
