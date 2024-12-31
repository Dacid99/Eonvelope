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

"""Module with the :class:`MailboxSerializer` serializer class."""

from rest_framework import serializers

from ...Models.MailboxModel import MailboxModel


class BaseMailboxSerializer(serializers.ModelSerializer):
    """The base serializer for :class:`Emailkasten.Models.MailboxModel.MailboxModel`.
    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`Emailkasten.Models.MailboxModel.MailboxModel` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.
        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        The read_only_fields must not be shortened in subclasses.
        """

        model = MailboxModel
        """The model to serialize."""

        fields = '__all__'
        """Includes all fields."""

        read_only_fields = ['name', 'account', 'is_healthy', 'created', 'updated']
        """The :attr:`Emailkasten.Models.MailboxModel.MailboxModel.name`,
        :attr:`Emailkasten.Models.MailboxModel.MailboxModel.account`,
        :attr:`Emailkasten.Models.MailboxModel.MailboxModel.is_healthy`,
        :attr:`Emailkasten.Models.MailboxModel.MailboxModel.created` and
        :attr:`Emailkasten.Models.MailboxModel.MailboxModel.updated` fields are read-only.
        """
