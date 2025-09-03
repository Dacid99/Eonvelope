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

"""Module with the :class:`HealthMixin`."""

from django.db.models import BooleanField, DateTimeField, Model, TextField
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class HealthModelMixin(Model):
    """Mixin adding a `health` functionality to a model class."""

    is_healthy = BooleanField(
        null=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("health status"),
    )
    """Flags whether the model instance is subject to errors. `None` by default."""

    last_error = TextField(
        blank=True,
        default="",
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("last error"),
    )
    """The latest error in connection with the model instance."""

    last_error_occurred_at = DateTimeField(
        null=True,
        # Translators: Do not capitalize the very first letter unless your language requires it.
        verbose_name=_("time of last error occurrence"),
    )
    """The time of occurrence of the latest error."""

    class Meta:
        """Metadata class for the mixin, abstract to avoid makemigrations picking it up."""

        abstract = True

    def set_unhealthy(self, errormessage: str) -> None:
        """Sets the `is_healthy` flag to `False` and adds the `last_error` and its time.

        Args:
            error: The error causing the health change.
        """
        self.last_error = errormessage
        self.last_error_occurred_at = timezone.now()
        self.is_healthy = False
        self.save(update_fields=["is_healthy", "last_error", "last_error_occurred_at"])

    def set_healthy(self) -> None:
        """Sets the `is_healthy` flag to `True`."""
        self.is_healthy = True
        self.save(update_fields=["is_healthy"])
