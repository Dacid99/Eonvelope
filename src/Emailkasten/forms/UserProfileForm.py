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

"""Module with the :class:`BaseAccountSerializer` form class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.forms import ModelForm

from Emailkasten.models import UserProfile


if TYPE_CHECKING:
    from django.db.models import Model


class UserProfileForm(ModelForm):
    """The form for :class:`Emailkasten.models.UserProfile`.

    Exposes all fields from the model that may be changed by the user.
    """

    class Meta:
        """Metadata class for the form."""

        model: Final[type[Model]] = UserProfile
        """The model to serialize."""

        exclude: ClassVar[list[str]] = ["user"]
        """Exposes all fields other than the `user` foreign key."""

        localized_fields = "__all__"
        """Localize all fields."""
