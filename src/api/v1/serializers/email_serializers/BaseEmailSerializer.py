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

"""Module with the :class:`BaseEmailSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from rest_framework import serializers

from core.models import Email


if TYPE_CHECKING:
    from django.db.models import Model


class BaseEmailSerializer(serializers.ModelSerializer[Email]):
    """The base serializer for :class:`core.models.Email`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.Email` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = Email
        """The model to serialize."""

        exclude: ClassVar[list[str]] = ["eml_filepath"]
        """Exclude the :attr:`core.models.Email.Email.eml_filepath` field."""

        read_only_fields: Final[list[str]] = [
            "message_id",
            "datetime",
            "email_subject",
            "plain_bodytext",
            "html_bodytext",
            "in_reply_to",
            "references",
            "datasize",
            "correspondents",
            "mailbox",
            "headers",
            "x_spam",
            "created",
            "updated",
        ]
        """All fields except for :attr:`core.models.Email.Email.is_favorite`
        are read-only.
        """
