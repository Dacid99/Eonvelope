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

"""Module with the :class:`AccountSerializer` serializer class."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from ...Models.AccountModel import AccountModel
from ..MailboxSerializers.MailboxSerializer import MailboxSerializer


class AccountSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.AccountModel`.
    Uses all fields except :attr:`Emailkasten.Models.AccountModel.user`."""

    password = serializers.CharField(max_length=255, write_only=True)
    """The password field is set to write-only for security reasons."""

    mail_address = serializers.EmailField()
    """The password field is a :restframework::class:`serializers.EmailField` for automatic validation of input."""

    mailboxes = MailboxSerializer(many=True, read_only=True)
    """The mailboxes of the account are serialized by :class:`Emailkasten.Models.MailboxSerializer`."""


    class Meta:
        """Metadata class for the serializer."""

        model = AccountModel

        exclude = ['user']
        """Exclude the :attr:`Emailkasten.Models.AccountModel.user` field."""

        read_only_fields = ['is_healthy', 'created', 'updated']
        """The :attr:`Emailkasten.Models.AccountModel.is_healthy`, :attr:`Emailkasten.Models.AccountModel.created`, and :attr:`Emailkasten.Models.AccountModel.updated` fields are read-only."""

        validators = [
            UniqueTogetherValidator(
                queryset=AccountModel.objects.all(),
                fields=['mail_address', 'user'],
                message='This account already exists!'
            )
        ]

    def validate_mail_address(self, value: str) -> str:
        """Validation step, sets the mailaddress to lower case.

        Args:
            value: The mail address given by the user.

        Returns:
            The given mail address in lower case.
        """
        return value.lower()
