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

from ...Models.DaemonModel import DaemonModel


class DaemonSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.DaemonModel`.
    Uses all fields except :attr:`Emailkasten.Models.DaemonModel.mailbox` and :attr:`Emailkasten.Models.DaemonModel.log_filepath` fields."""

    class Meta:
        model = DaemonModel

        exclude = ['log_filepath']
        """Exclude the :attr:`Emailkasten.Models.DaemonModel.log_filepath` field."""

        read_only_fields = ['is_running', 'is_healthy', 'created', 'updated']
        """The :attr:`Emailkasten.Models.DaemonModel.is_running`, :attr:`Emailkasten.Models.DaemonModel.is_healthy`, :attr:`Emailkasten.Models.DaemonModel.created`, and :attr:`Emailkasten.Models.DaemonModel.updated` fields are read-only."""


    def validate_fetching_criterion(self, value: str) -> str:
        """Check whether the fetching criterion is available for the mailbox of the serialized daemon.

        Args:
            value: The given fetching criterion.

        Returns:
            The validated fetching criterion.

        Raises:
            :restframework::class:`serializers.ValidationError`: If the given fetching criterion is not available for the daemon.
        """
        if self.instance and self.instance.mailbox and value not in self.instance.mailbox.getAvailableFetchingCriteria():
            raise serializers.ValidationError("Fetching criterion not available for this mailbox!")
        return value
