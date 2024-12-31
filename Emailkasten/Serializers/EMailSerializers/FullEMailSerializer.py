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

"""Module with the :class:`FullEMailSerializer` serializer class."""

from rest_framework import serializers
from rest_framework.utils.serializer_helpers import ReturnDict

from ...Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ...Models.EMailModel import EMailModel
from ..AttachmentSerializers.AttachmentSerializer import AttachmentSerializer
from ..EMailCorrespondentsSerializers.EMailCorrespondentsSerializer import \
    EMailCorrespondentSerializer
from ..ImageSerializers.ImageSerializer import ImageSerializer
from ..MailingListSerializers.SimpleMailingListSerializer import \
    SimpleMailingListSerializer


class FullEMailSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.EMailModel`.
    Uses all fields including all correspondents and mailinglists mentioning the correspondent as well as all images and attachments.
    Use exclusively in a :restframework::class:`viewsets.ReadOnlyModelViewSet`."""

    attachments = AttachmentSerializer(many=True, read_only=True)
    """The attachments are serialized by :class:`Emailkasten.AttachmentSerializers.AttachmentSerializer.AttachmentSerializer`."""

    images = ImageSerializer(many=True, read_only=True)
    """The images are serialized by :class:`Emailkasten.ImageSerializers.ImageSerializer.ImageSerializer`."""

    mailinglist = SimpleMailingListSerializer(read_only=True)
    """The attachments are serialized by :class:`Emailkasten.MailingListSerializers.SimpleMailingListSerializer.SimpleMailingListSerializer`."""

    correspondents = serializers.SerializerMethodField(read_only=True)
    """The emails are set from the :class:`Emailkasten.Models.EMailCorrespondentsModel` via :func:`get_emails`."""


    class Meta:
        """Metadata class for the serializer."""

        model = EMailModel

        exclude = ['eml_filepath', 'prerender_filepath']
        """Exclude the :attr:`Emailkasten.Models.EMailModel.eml_filepath` and :attr:`Emailkasten.Models.EMailModel.prerender_filepath` fields."""

        read_only_fields = [
            'message_id',
            'datetime',
            'email_subject',
            'bodytext',
            'inReplyTo',
            'datasize',
            'account',
            'comments',
            'keywords',
            'importance',
            'priority',
            'precedence',
            'received',
            'user_agent',
            'auto_submitted',
            'content_type',
            'content_language',
            'content_location',
            'x_priority',
            'x_originated_client',
            'x_spam',
            'created',
            'updated',
            'attachments',
            'images',
            'mailinglist',
            'correspondents'
        ]


    def get_correspondents(self, object: EMailModel) -> ReturnDict|None:
        """Serializes the correspondents connected to the instance to be serialized.

        Args:
            object: The instance being serialized.

        Returns:
            The serialized correspondents connected to the instance to be serialized.
            None if the the user is not authenticated.
        """
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            emailcorrespondents = EMailCorrespondentsModel.objects.filter(email=object, email__account__user=user).distinct()
            return EMailCorrespondentSerializer(emailcorrespondents, many=True, read_only=True).data
        else:
            return None
