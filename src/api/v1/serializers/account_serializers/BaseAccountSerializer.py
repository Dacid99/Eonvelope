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

"""Module with the :class:`BaseAccountSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from rest_framework import serializers

from core.models import Account


if TYPE_CHECKING:
    from django.db.models import Model


class BaseAccountSerializer(serializers.ModelSerializer[Account]):
    """The base serializer for :class:`core.models.Account`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.Account` should inherit from this.
    """

    password = serializers.CharField(max_length=255, write_only=True)
    """The :attr:`core.models.Account.Account.password` field
    is set to write-only for security reasons.
    """

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    """The :attr:`core.models.Account.Account.user` field is included but hidden."""

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = Account
        """The model to serialize."""

        fields = "__all__"
        """Include all fields."""

        read_only_fields: Final[list[str]] = ["is_healthy", "created", "updated"]
        """The :attr:`core.models.Account.Account.is_healthy`,
        :attr:`core.models.Account.Account.created` and
        :attr:`core.models.Account.Account.updated` fields are read-only.
        """
