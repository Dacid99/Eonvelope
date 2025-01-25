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

"""Module with the :class:`ConfigurationSerializer` serializer class."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from core.models.ConfigurationModel import ConfigurationModel


class ConfigurationSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`core.models.AccountModel`."""

    class Meta:
        """Metadata class for the serializer."""

        model = ConfigurationModel

        fields = '__all__'
        """Include all fields."""

        read_only_fields = ['created', 'updated']
        """The :attr:`core.models.AccountModel.created`, and :attr:`core.models.AccountModel.updated` fields are read-only."""

        validators = [
            UniqueTogetherValidator(
                queryset=ConfigurationModel.objects.all(),
                fields=['category', 'key'],
                message='This configuration already exists!'
            )
        ]
