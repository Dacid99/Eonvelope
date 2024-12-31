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

from rest_framework import serializers

from ...Models.MailingListModel import MailingListModel
from ..CorrespondentSerializers.BaseCorrespondentSerializer import \
    BaseCorrespondentSerializer
from ..EMailSerializers.BaseEMailSerializer import BaseEMailSerializer
from .BaseMailingListSerializer import BaseMailingListSerializer


class MailingListSerializer(BaseMailingListSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.MailingList`.
    Includes nested serializers for the :attr:`Emailkasten.Models.MailingList.MailingList.emails`,
    :attr:`Emailkasten.Models.MailingList.MailingList.correspondent` foreign key fields
    as well as a method field for the count of elements in :attr:`Emailkasten.Models.MailingList.MailingList.emails`.
    """

    emails = BaseEMailSerializer(many=True, read_only=True)
    """The emails from the mailinglist are serialized
    by :class:`Emailkasten.Serializers.EMailSerializers.BaseEMailSerializer.BaseEMailSerializer`.
    """

    correspondent = BaseCorrespondentSerializer(read_only=True)
    """The correspondent sending the mailinglist are serialized
    by :class:`Emailkasten.Serializers.CorrespondentSerializers.BaseCorrespondentSerializer.BaseCorrespondentSerializer`.
    """

    email_number = serializers.SerializerMethodField(read_only=True)
    """The number of mails by the mailinglist. Set via :func:`get_email_number`."""


    class Meta(BaseMailingListSerializer.Meta):
        """Metadata class for the serializer."""


    def get_email_number(self, object: MailingListModel) -> int:
        """Gets the number of mails sent by the mailinglist.

        Args:
            object:  The instance being serialized.

        Returns:
            The number of mails referencing by the instance.
        """
        number = object.emails.count()
        return number
