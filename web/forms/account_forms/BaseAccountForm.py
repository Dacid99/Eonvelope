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

"""Module with the :class:`BaseAccountSerializer` form class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

from django.forms import PasswordInput, Widget

from core.models.Account import Account

from ...utils.forms import RequiredMarkerModelForm


if TYPE_CHECKING:
    from django.db.models import Model


class BaseAccountForm(RequiredMarkerModelForm):
    """The base form for :class:`core.models.Account.Account`.

    Exposes all fields from the model that may be changed by the user.
    Other forms for :class:`core.models.Account.Account` should inherit from this.
    """

    class Meta:
        """Metadata class for the base form.

        Other form metaclasses should inherit from this.
        These submetaclasses must not expose fields that are not listed here.
        """

        model: Final[type[Model]] = Account
        """The model to serialize."""

        fields: ClassVar[list[str]] = [
            "mail_address",
            "password",
            "mail_host",
            "protocol",
            "mail_host_port",
            "timeout",
            "is_favorite",
        ]
        """Exposes all fields that the user should be able to change."""

        widgets: ClassVar[dict[str, type[Widget]]] = {
            "password": PasswordInput,
        }
