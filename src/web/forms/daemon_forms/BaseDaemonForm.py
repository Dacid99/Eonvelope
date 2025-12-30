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

"""Module with the :class:`BaseDaemonForm` form class."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, ClassVar, Final, override

from django import forms
from django_celery_beat.models import IntervalSchedule

from core.models import Daemon
from web.utils.forms import RequiredMarkerModelForm


if TYPE_CHECKING:
    from django.db.models import Model


class BaseDaemonForm(RequiredMarkerModelForm):
    """The base form for :class:`core.models.Daemon`.

    Exposes all fields from the model that may be changed by the user.
    Other forms for :class:`core.models.Daemon` should inherit from this.
    """

    interval_every = forms.IntegerField(
        min_value=1,
        required=True,
        label=IntervalSchedule._meta.get_field(  # noqa: SLF001 ; this is required for consistent labeling
            "every"
        ).verbose_name,
        help_text=IntervalSchedule._meta.get_field(  # noqa: SLF001 ; this is required for consistent labeling
            "every"
        ).help_text,
    )
    interval_period = forms.ChoiceField(
        choices=IntervalSchedule.PERIOD_CHOICES,
        required=True,
        label=IntervalSchedule._meta.get_field(  # noqa: SLF001 ; this is required for consistent labeling
            "period"
        ).verbose_name,
        help_text=IntervalSchedule._meta.get_field(  # noqa: SLF001 ; this is required for consistent labeling
            "period"
        ).help_text,
    )

    class Meta:
        """Metadata class for the base form.

        Other form metaclasses should inherit from this.
        These submetaclasses must not expose fields that are not listed here.
        """

        model: Final[type[Model]] = Daemon
        """The model to serialize."""

        fields: ClassVar[list[str]] = [
            "fetching_criterion",
            "fetching_criterion_arg",
        ]
        """Exposes all fields that the user should be able to change."""

        localized_fields = "__all__"
        """Localize all fields."""

    @override
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        with contextlib.suppress(Daemon.interval.RelatedObjectDoesNotExist):
            self.initial["interval_every"] = self.instance.interval.every
            self.initial["interval_period"] = self.instance.interval.period

    @override
    def save(self, commit: bool = True) -> Any:
        """Extended to add the intervaldata to the instance.

        Important:
            There should not be duplicate IntervalSchedules.
            https://django-celery-beat.readthedocs.io/en/latest/index.html#example-creating-interval-based-periodic-task
        """
        self.instance.interval, _ = IntervalSchedule.objects.get_or_create(
            every=self.cleaned_data["interval_every"],
            period=self.cleaned_data["interval_period"],
        )
        return super().save(commit)
