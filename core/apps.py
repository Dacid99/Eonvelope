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

"""The apps module for :mod:`core`."""
from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """App config for :mod:`core`."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self) -> None:
        """Imports all model signals."""
        # ruff: noqa: F401
        # pylint: disable=import-outside-toplevel, unused-import ; this is the way it is intended by django
        from .signals import (
            delete_DaemonModel,
            save_AccountModel,
            save_DaemonModel,
            save_MailboxModel,
        )
