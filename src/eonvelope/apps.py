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

"""The apps module for :mod:`core`."""

from __future__ import annotations

from typing import override

from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class EonvelopeAdminConfig(AdminConfig):
    """App config for django admin to set the custom site as default.

    References:
        https://docs.djangoproject.com/en/5.2/ref/contrib/admin/#overriding-the-default-admin-site
    """

    default_site = "eonvelope.admin.EonvelopeAdminSite"


class EonvelopeConfig(AppConfig):
    """App config for :mod:`eonvelope`."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "eonvelope"

    @override
    def ready(self) -> None:
        """Imports all model signals."""
        # ruff: noqa: F401,PLC0415
        # pylint: disable=import-outside-toplevel, unused-import  # this is the way it is intended by django
        import eonvelope.signals
