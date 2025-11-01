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

"""Module with the :class:`web.views.EmailTableView` view."""

from django.db.models import QuerySet
from django_tables2.views import SingleTableMixin

from web.tables.email_tables.BaseEmailTable import BaseEmailTable

from .EmailFilterView import EmailFilterView


class EmailTableView(SingleTableMixin, EmailFilterView):
    """View for filtering a table of :class:`core.models.Email` instances."""

    URL_NAME = "email-table"
    template_name = "web/email/email_table.html"
    table_class = BaseEmailTable

    def get_paginate_by(self, table_data: QuerySet) -> int | None:
        """Overridden to reconcile mixin and view."""
        return EmailFilterView.get_paginate_by(self, table_data)
