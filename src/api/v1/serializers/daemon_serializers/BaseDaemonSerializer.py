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

"""Module with the :class:`BaseDaemonSerializer` serializer class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Final, override

from django.core.exceptions import ValidationError
from django_celery_beat.models import IntervalSchedule
from rest_framework import serializers

from api.v1.serializers.django_celery_beat_serializers import (
    IntervalScheduleSerializer,
    PeriodicTaskSerializer,
)
from core.models import Daemon


if TYPE_CHECKING:
    from django.db.models import Model


class BaseDaemonSerializer(serializers.ModelSerializer[Daemon]):
    """The base serializer for :class:`core.models.Daemon`.

    Includes all viable fields from the model.
    Sets all constraints that must be implemented in all serializers.
    Other serializers for :class:`core.models.Daemon` should inherit from this.
    """

    interval = IntervalScheduleSerializer()
    """The interval is serialized
    by :class:`api.v1.serializers.django_celery_beat_serializers.IntervalScheduleSerializer`.
    It can be altered.
    """
    celery_task = PeriodicTaskSerializer(read_only=True)
    """The celery_task is serialized
    by :class:`api.v1.serializers.django_celery_beat_serializers.PeriodicTaskSerializer`.
    """

    class Meta:
        """Metadata class for the base serializer.

        Contains constraints that must be implemented by all serializers.
        Other serializer metaclasses should inherit from this.
        :attr:`read_only_fields` and :attr:`exclude` must not be shortened in subclasses.
        """

        model: Final[type[Model]] = Daemon
        """The model to serialize."""

        fields: ClassVar[str] = "__all__"
        """Include all fields."""

        read_only_fields: Final[list[str]] = [
            "uuid",
            "is_healthy",
            "last_error",
            "last_error_occurred_at",
            "created",
            "updated",
        ]
        """The :attr:`core.models.Daemon.Daemon.uuid`,
        :attr:`core.models.Daemon.Daemon.is_healthy`,
        :attr:`core.models.Daemon.Daemon.created` and
        :attr:`core.models.Daemon.Daemon.updated` fields are read-only.
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
        except ValidationError as error:
            raise serializers.ValidationError(
                error.message_dict or error.messages
            ) from error

        return attrs

    @override
    def update(self, instance: Daemon, validated_data: dict) -> Daemon:
        """Extended to add the intervaldata to the instance.

        Important:
            The nested intervaldata must be popped as update does not support nested dicts!
            There should not be duplicate IntervalSchedules.
            https://django-celery-beat.readthedocs.io/en/latest/index.html#example-creating-interval-based-periodic-task
        """
        interval_data = validated_data.pop("interval", None)
        if interval_data:
            instance.interval, _ = IntervalSchedule.objects.get_or_create(
                every=interval_data["every"],
                period=interval_data["period"],
            )
        return super().update(instance, validated_data)

    @override
    def create(self, validated_data: dict) -> Daemon:
        """Extended to add the intervaldata to the instance.

        Important:
            The nested intervaldata must be popped as create does not support nested dicts!
            There should not be duplicate IntervalSchedules.
            https://django-celery-beat.readthedocs.io/en/latest/index.html#example-creating-interval-based-periodic-task
        """
        interval_data = validated_data.pop("interval")
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=interval_data["every"],
            period=interval_data["period"],
        )
        return super().create({**validated_data, "interval": interval})
