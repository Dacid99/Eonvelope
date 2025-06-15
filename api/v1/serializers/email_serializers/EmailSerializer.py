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

"""Module with the :class:`EmailSerializer` serializer class."""

# ruff: noqa: TC001 TC002
# TYPE_CHECKING guard doesn't work with drf-spectacular: https://github.com/tfranzel/drf-spectacular/issues/390

from __future__ import annotations

from typing import Any, ClassVar

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from core.models import Email

from ..attachment_serializers import BaseAttachmentSerializer
from ..emailcorrespondent_serializers.EmailCorrespondentSerializer import (
    EmailCorrespondentSerializer,
)
from .BaseEmailSerializer import BaseEmailSerializer


class EmailSerializer(BaseEmailSerializer):
    """The standard serializer for a :class:`core.models.Email`.

    Includes only the most relevant model fields.
    Includes nested serializers for the :attr:`core.models.Email.Email.replies`,
    :attr:`core.models.Email.Email.attachments`and
    :attr:`core.models.Email.Email.correspondents` foreign key and related fields.
    """

    replies: serializers.PrimaryKeyRelatedField[Email] = (
        serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    )
    """The replies mails are included by id only to prevent recursion."""

    referenced_by: serializers.PrimaryKeyRelatedField[Email] = (
        serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    )
    """The referencing mails are included by id only to prevent recursion."""

    attachments = BaseAttachmentSerializer(many=True, read_only=True)
    """The attachments are serialized
    by :class:`Emailkasten.AttachmentSerializers.BaseAttachmentSerializer.BaseAttachmentSerializer`.
    """

    correspondents = serializers.SerializerMethodField(read_only=True)
    """The emails are set from the
    :class:`core.models.EmailCorrespondent`
    via :func:`get_correspondents`.
    """

    class Meta(BaseEmailSerializer.Meta):
        """Metadata class for the serializer."""

        exclude: ClassVar[list[str]] = [*BaseEmailSerializer.Meta.exclude, "headers"]
        """Omit the other header fields."""

    def get_correspondents(self, instance: Email) -> ReturnDict[str, Any]:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            instance: The instance being serialized.

        Returns:
            The serialized correspondents connected to the instance to be serialized.
        """
        emailcorrespondents = instance.emailcorrespondents.all().distinct()
        return EmailCorrespondentSerializer(
            emailcorrespondents, many=True, read_only=True
        ).data
