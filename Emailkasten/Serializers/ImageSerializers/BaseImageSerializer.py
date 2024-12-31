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

"""Module with the :class:`ImageSerializer` serializer class."""

from rest_framework import serializers

from ...Models.ImageModel import ImageModel


class BaseImageSerializer(serializers.ModelSerializer):
    """The base serializer for :class:`Emailkasten.Models.ImageModel.ImageModel`.
    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`Emailkasten.Models.ImageModel.ImageModel` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.
        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        The read_only_fields must not be shortened in subclasses.
        """

        model = ImageModel
        """The model to serialize."""

        exclude = ['file_path']
        """Exclude the :attr:`Emailkasten.Models.ImageModel.ImageModel.file_path` field."""

        read_only_fields = [
                'file_name',
                'datasize',
                'email',
                'created',
                'updated'
            ]
        """The :attr:`Emailkasten.Models.ImageModel.ImageModel.is_healthy`,
        :attr:`Emailkasten.Models.ImageModel.ImageModel.datasize`,
        :attr:`Emailkasten.Models.ImageModel.ImageModel.email`,
        :attr:`Emailkasten.Models.ImageModel.ImageModel.created` and
        :attr:`Emailkasten.Models.ImageModel.ImageModel.updated` fields are read-only.
        """
