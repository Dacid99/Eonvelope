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

"""Module with the :class:`BaseDaemonSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from rest_framework import serializers

from core.models.DaemonModel import DaemonModel


if TYPE_CHECKING:
    from django.db.models import Model


class BaseDaemonSerializer(serializers.ModelSerializer):
    """The base serializer for :class:`core.models.DaemonModel.DaemonModel`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.DaemonModel.DaemonModel` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = DaemonModel
        """The model to serialize."""

        exclude: ClassVar[list[str]] = ["log_filepath"]
        """Exclude the :attr:`core.models.DaemonModel.log_filepath` field."""

        read_only_fields: Final[list[str]] = [
            "uuid",
            "mailbox",
            "is_running",
            "is_healthy",
            "created",
            "updated",
        ]
        """The :attr:`core.models.DaemonModel.DaemonModel.uuid`,
        :attr:`core.models.DaemonModel.DaemonModel.mailbox`,
        :attr:`core.models.DaemonModel.DaemonModel.is_running`,
        :attr:`core.models.DaemonModel.DaemonModel.is_healthy`,
        :attr:`core.models.DaemonModel.DaemonModel.created` and
        :attr:`core.models.DaemonModel.DaemonModel.updated` fields are read-only.
        """

    def validate_fetching_criterion(self, value: str) -> str:
        """Check whether the fetching criterion is available for the mailbox of the serialized daemon.

        Args:
            value: The given fetching criterion.

        Returns:
            The validated fetching criterion.

        Raises:
            :restframework::class:`serializers.ValidationError`: If the given fetching criterion is not available for the daemon.
        """
        if (
            self.instance
            and self.instance.mailbox
            and value not in self.instance.mailbox.getAvailableFetchingCriteria()
        ):
            raise serializers.ValidationError(
                "Fetching criterion not available for this mailbox!"
            )
        return value
