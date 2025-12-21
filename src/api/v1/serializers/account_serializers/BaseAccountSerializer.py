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

"""Module with the :class:`BaseAccountSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, override

from django.core.exceptions import ValidationError
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

        read_only_fields: Final[list[str]] = [
            "is_healthy",
            "last_error",
            "last_error_occurred_at",
            "created",
            "updated",
        ]
        """The :attr:`core.models.Account.Account.is_healthy`,
        :attr:`core.models.Account.Account.created` and
        :attr:`core.models.Account.Account.updated` fields are read-only.
        """

        extra_kwargs = {"password": {"write_only": True}}
        """The :attr:`core.models.Account.Account.password` field
        is set to write-only for security reasons.
        """

    @override
    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Include full model-side validation to allow testing of account on submission.

        Args:
            attrs: The attributes on the serializer.

        Returns:
            The same attributes.

        Raises:
            serializers.ValidationError: If the validation fails.
        """
        instance = self.instance or self.Meta.model()

        for attr, value in attrs.items():
            setattr(instance, attr, value)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)

        return attrs
