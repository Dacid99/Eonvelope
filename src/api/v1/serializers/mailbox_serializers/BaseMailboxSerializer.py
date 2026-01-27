# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Module with the :class:`BaseMailboxSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from rest_framework import serializers

from core.models import Mailbox

if TYPE_CHECKING:
    from django.db.models import Model


class BaseMailboxSerializer(serializers.ModelSerializer[Mailbox]):
    """The base serializer for :class:`core.models.Mailbox`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.Mailbox` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = Mailbox
        """The model to serialize."""

        fields = "__all__"
        """Includes all fields."""

        read_only_fields: Final[list[str]] = [
            "name",
            "type",
            "account",
            "is_healthy",
            "last_error",
            "last_error_occurred_at",
            "created",
            "updated",
        ]
        """The :attr:`core.models.Mailbox.Mailbox.name`,
        :attr:`core.models.Mailbox.Mailbox.type`,
        :attr:`core.models.Mailbox.Mailbox.account`,
        :attr:`core.models.Mailbox.Mailbox.is_healthy`,
        :attr:`core.models.Mailbox.Mailbox.created` and
        :attr:`core.models.Mailbox.Mailbox.updated` fields are read-only.
        """
