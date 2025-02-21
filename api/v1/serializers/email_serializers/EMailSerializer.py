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

"""Module with the :class:`EMailSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from rest_framework import serializers

from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel

from ..attachment_serializers.BaseAttachmentSerializer import BaseAttachmentSerializer
from ..emailcorrespondents_serializers.EMailCorrespondentsSerializer import (
    EMailCorrespondentSerializer,
)
from ..mailinglist_serializers.SimpleMailingListSerializer import (
    SimpleMailingListSerializer,
)
from .BaseEMailSerializer import BaseEMailSerializer


if TYPE_CHECKING:
    from rest_framework.utils.serializer_helpers import ReturnDict

    from core.models.EMailModel import EMailModel


class EMailSerializer(BaseEMailSerializer):
    """The standard serializer for a :class:`core.models.EMailModel`.

    Includes only the most relevant model fields.
    Includes nested serializers for the :attr:`core.models.EMailModel.EMailModel.replies`,
    :attr:`core.models.EMailModel.EMailModel.attachments`,
    :attr:`core.models.EMailModel.EMailModel.mailinglist` and
    :attr:`core.models.EMailModel.EMailModel.correspondents` foreign key and related fields.
    """

    replies = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    """The replies mails are included by id only to prevent recursion."""

    attachments = BaseAttachmentSerializer(many=True, read_only=True)
    """The attachments are serialized
    by :class:`Emailkasten.AttachmentSerializers.BaseAttachmentSerializer.BaseAttachmentSerializer`.
    """

    mailinglist = SimpleMailingListSerializer(read_only=True)
    """The attachments are serialized
    by :class:`Emailkasten.MailingListSerializers.SimpleMailingListSerializer.SimpleMailingListSerializer`.
    """

    correspondents = serializers.SerializerMethodField(read_only=True)
    """The emails are set from the
    :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`
    via :func:`get_emails`.
    """

    class Meta(BaseEMailSerializer.Meta):
        """Metadata class for the serializer."""

        exclude: ClassVar[list[str]] = [*BaseEMailSerializer.Meta.exclude, "headers"]
        """Omit the other header fields."""

    def get_correspondents(self, object: EMailModel) -> ReturnDict | None:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            object: The instance being serialized.

        Returns:
            The serialized correspondents connected to the instance to be serialized.
            An empty list if the the user is not authenticated.
        """
        request = self.context.get("request")
        user = request.user if request else None
        if user is not None:
            emailcorrespondents = EMailCorrespondentsModel.objects.filter(
                email=object, email__mailbox__account__user=user
            ).distinct()
            return EMailCorrespondentSerializer(
                emailcorrespondents, many=True, read_only=True
            ).data
        return []
