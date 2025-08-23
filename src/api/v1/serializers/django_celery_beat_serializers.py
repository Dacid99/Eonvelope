# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""Module with serializers for the :mod:`django_celery_beat.models` models."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django_celery_beat.models import IntervalSchedule, PeriodicTask
from rest_framework import serializers


if TYPE_CHECKING:
    from django.db.models import Model


class IntervalScheduleSerializer(serializers.ModelSerializer[IntervalSchedule]):
    """The base serializer for :class:`django_celery_beat.models.IntervalSchedule`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`django_celery_beat.models.IntervalSchedule` should inherit from this.
    """

    class Meta:
        """Metadata class for the serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = IntervalSchedule
        """The model to serialize."""

        fields = "__all__"
        """Include all fields."""


class PeriodicTaskSerializer(serializers.ModelSerializer[PeriodicTask]):
    """The base serializer for :class:`django_celery_beat.models.PeriodicTask`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`django_celery_beat.models.PeriodicTask` should inherit from this.
    """

    class Meta:
        """Metadata class for the serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = PeriodicTask
        """The model to serialize."""

        fields: ClassVar[list[str]] = ["enabled", "last_run_at", "total_run_count"]
        """Include only the :attr:`django_celery_beat.models.PeriodicTask.enabled`,
        :attr:`django_celery_beat.models.PeriodicTask.last_run_at`,
        :attr:`django_celery_beat.models.PeriodicTask.total_run_count` fields.
        """

        read_only_fields: Final[list[str]] = fields
        """All fields are read-only"""
