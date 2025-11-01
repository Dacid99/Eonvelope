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

"""test.web.tables.attachment_tables package containing attachment tables of the Emailkasten webapp."""

from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import Attachment
from web.utils.columns import CheckboxColumn, IsFavoriteColumn


class BaseAttachmentTable(Table):
    file_name = Column(linkify=True)
    checkbox = CheckboxColumn()
    is_favorite = IsFavoriteColumn()
    email = Column(
        verbose_name=_("Email"),
        linkify=lambda record: record.email.get_absolute_url(),
        accessor="email__subject",
    )
    content_type = Column(order_by=("content_maintype", "content_subtype"))

    class Meta:
        model = Attachment
        fields = (
            "is_favorite",
            "file_name",
            "email",
            "content_disposition",
            "content_id",
            "content_type",
            "datasize",
        )
        sequence = ("checkbox", *fields)

    def render_datasize(self, value):
        return str(value) + " " + _("bytes")
