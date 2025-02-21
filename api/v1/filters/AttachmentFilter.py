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

"""Module with the :class:`AttachmentFilter` filter set class."""

from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Final

import django_filters

from api.constants import FilterSetups
from core.models.AttachmentModel import AttachmentModel


if TYPE_CHECKING:
    from django.db.models import Model


class AttachmentFilter(django_filters.FilterSet):
    """The filter class for :class:`core.models.AttachmentModel`."""

    class Meta:
        """Metadata class for the filter."""

        model: Final[type[Model]] = AttachmentModel

        fields: ClassVar[dict[str, list[str]]] = {
            "file_name": FilterSetups.TEXT,
            "content_disposition": FilterSetups.TEXT,
            "content_type": FilterSetups.TEXT,
            "datasize": FilterSetups.INT,
            "is_favorite": FilterSetups.BOOL,
            "created": FilterSetups.DATETIME,
            "updated": FilterSetups.DATETIME,
            "email__datetime": FilterSetups.DATETIME,
        }
