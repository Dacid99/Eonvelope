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

""":mod:`web.views.email_views.archive_views.EmailArchiveMixin` module with the EmailArchiveMixin mixin."""

from django.db.models import QuerySet

from core.models import Email
from web.mixins import PageSizeMixin


class EmailArchiveMixin(PageSizeMixin):
    """Mixin defining common attributes of the ArchiveViews for emails."""

    BASE_URL_NAME = "email-archive"
    BASE_TEMPLATE_NAME = "web/email/archive/"
    model = Email
    date_field = "datetime"
    ordering = "datetime"
    make_object_list = True
    allow_empty = True
    allow_future = True

    def get_queryset(self) -> QuerySet[Email]:
        """Restricts the queryset to objects owned by the requesting user."""
        return (
            super()
            .get_queryset()
            .filter(mailbox__account__user=self.request.user)
            .select_related("mailbox", "mailbox__account")
        )
