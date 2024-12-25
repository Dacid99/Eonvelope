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

"""Module with the :class:`SimpleEMailSerializer` serializer class."""

from rest_framework import serializers

from ...Models.EMailModel import EMailModel


class SimpleEMailSerializer(serializers.ModelSerializer):
    """A reduced serializer for a :class:`Emailkasten.Models.EMailModel`.
    Uses all fields excluding including the correspondents, the mailinglist and all images and attachments..
    Use exclusively in a :restframework::class:`viewsets.ReadOnlyModelViewSet`."""

    class Meta:
        """Metadata class for the serializer."""

        model = EMailModel

        exclude = ['eml_filepath', 'prerender_filepath']
        """Exclude the :attr:`Emailkasten.Models.EMailModel.eml_filepath` and :attr:`Emailkasten.Models.EMailModel.prerender_filepath` fields."""
