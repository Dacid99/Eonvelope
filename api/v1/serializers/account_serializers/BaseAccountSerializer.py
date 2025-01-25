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

from core.models.AccountModel import AccountModel


class BaseAccountSerializer(serializers.ModelSerializer):
    """The base serializer for :class:`core.models.AccountModel.AccountModel`.
    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.AccountModel.AccountModel` should inherit from this.
    """

    password = serializers.CharField(max_length=255, write_only=True)
    """The :attr:`core.models.AccountModel.AccountModel.password` field
    is set to write-only for security reasons.
    """

    mail_address = serializers.EmailField()
    """The :attr:`core.models.AccountModel.AccountModel.mail_address` field
    is a :restframework::class:`serializers.EmailField` for automatic validation of input.
    """

    class Meta:
        """Metadata class for the base serializer.
        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        The read_only_fields must not be shortened in subclasses.
        """

        model = AccountModel
        """The model to serialize."""

        exclude = ['user']
        """Exclude the :attr:`core.models.AccountModel.AccountModel.user` field."""

        read_only_fields = ['is_healthy', 'created', 'updated']
        """The :attr:`core.models.AccountModel.AccountModel.is_healthy`,
        :attr:`core.models.AccountModel.AccountModel.created` and
        :attr:`core.models.AccountModel.AccountModel.updated` fields are read-only.
        """
