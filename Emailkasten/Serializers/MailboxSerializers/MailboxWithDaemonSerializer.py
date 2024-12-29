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

"""Module with the :class:`MailboxWithDaemonsSerializer` serializer class."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ...Models.MailboxModel import MailboxModel
from ..DaemonSerializers.DaemonSerializer import DaemonSerializer


class MailboxWithDaemonSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.DaemonModel`.
    Uses all fields including the daemon."""

    daemons = DaemonSerializer(many=True, read_only=True)
    """The emails are serialized by :class:`Emailkasten.Serializers.DaemonSerializers.DaemonSerializer`."""


    class Meta:
        """Metadata class for the serializer."""

        model = MailboxModel

        fields = '__all__'
        """Includes all fields."""

        read_only_fields = ['name', 'account', 'is_healthy', 'created', 'updated', 'daemons']

        validators = [
            UniqueTogetherValidator(
                queryset=MailboxModel.objects.all(),
                fields=['name', 'account'],
                message='This mailbox already exists!'
            )
        ]
