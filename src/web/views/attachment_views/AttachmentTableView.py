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

"""Module with the :class:`web.views.AttachmentTableView` view."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from django_tables2.views import SingleTableMixin

from web.tables.attachment_tables.BaseAttachmentTable import BaseAttachmentTable

from .AttachmentFilterView import AttachmentFilterView

if TYPE_CHECKING:
    from django.db.models import QuerySet


class AttachmentTableView(SingleTableMixin, AttachmentFilterView):
    """View for filtering a table of :class:`core.models.Attachment` instances."""

    URL_NAME = "attachment-table"
    template_name = "web/attachment/attachment_table.html"
    table_class = BaseAttachmentTable

    @override
    def get_paginate_by(self, table_data: QuerySet) -> int:
        """Overridden to reconcile mixin and view."""
        return AttachmentFilterView.get_paginate_by(self, table_data)
