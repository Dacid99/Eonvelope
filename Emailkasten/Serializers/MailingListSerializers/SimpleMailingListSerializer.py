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

from rest_framework import serializers

from ...Models.MailingListModel import MailingListModel


class SimpleMailingListSerializer(serializers.ModelSerializer):
    """A reduced serializer for a :class:`Emailkasten.Models.MailingListModel`.
    Uses all fields excluding the mails and the correspondent.
    Use exclusively in a :restframework::class:`viewsets.ReadOnlyModelViewSet`."""

    email_number = serializers.SerializerMethodField()
    """The number of mails by the mailinglist. Set via :func:`get_email_number`."""


    class Meta:
        model = MailingListModel

        fields = '__all__'
        """Include all fields."""


    def get_email_number(self, object: MailingListModel) -> int:
        """Gets the number of mails sent by the mailinglist.

        Args:
            object:  The instance being serialized.

        Returns:
           The number of mails referencing by the instance.
        """
        number = object.emails.count()
        return number
