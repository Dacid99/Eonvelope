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


class ImageSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.ImageModel`.
    Uses all fields except :attr:`Emailkasten.Models.ImageModel.file_path`.
    Use exclusively in a :restframework::class:`viewsets.ReadOnlyModelViewSet`."""

    class Meta:
        """Metadata class for the serializer."""

        model = ImageModel

        exclude = ['file_path']
        """Exclude the :attr:`Emailkasten.Models.ImageModel.file_path` field."""

        read_only_fields = [
                'file_name',
                'datasize',
                'email',
                'created',
                'updated'
            ]
