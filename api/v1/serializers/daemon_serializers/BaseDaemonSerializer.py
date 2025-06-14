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

from core.models import Daemon


if TYPE_CHECKING:
    from django.db.models import Model


class BaseDaemonSerializer(serializers.ModelSerializer[Daemon]):
    """The base serializer for :class:`core.models.Daemon`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.Daemon` should inherit from this.
    """

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = Daemon
        """The model to serialize."""

        exclude: ClassVar[list[str]] = ["log_filepath", "celery_task"]
        """Exclude the :attr:`core.models.Daemon` field."""

        read_only_fields: Final[list[str]] = [
            "uuid",
            "mailbox",
            "interval",
            "is_healthy",
            "created",
            "updated",
        ]
        """The :attr:`core.models.Daemon.Daemon.uuid`,
        :attr:`core.models.Daemon.Daemon.mailbox`,
        :attr:`core.models.Daemon.Daemon.interval`,
        :attr:`core.models.Daemon.Daemon.is_healthy`,
        :attr:`core.models.Daemon.Daemon.created` and
        :attr:`core.models.Daemon.Daemon.updated` fields are read-only.
        """
