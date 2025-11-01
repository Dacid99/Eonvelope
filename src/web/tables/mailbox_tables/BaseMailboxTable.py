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

"""Module with the :class:`web.tables.BaseAccountTable` table class."""

from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import Mailbox
from web.utils.columns import CheckboxColumn, IsFavoriteColumn, IsHealthyColumn


class BaseMailboxTable(Table):
    """Table class for :class:`core.models.Mailbox.Mailbox`."""

    checkbox = CheckboxColumn()
    is_favorite = IsFavoriteColumn()
    is_healthy = IsHealthyColumn()
    name = Column(linkify=True)
    account = Column(
        verbose_name=_("Account"),
        linkify=lambda record: record.account.get_absolute_url(),
        accessor="account__mail_address",
    )

    class Meta:
        """Metadata class for the table."""

        model = Mailbox
        fields = (
            "is_favorite",
            "name",
            "account",
            "save_attachments",
            "save_to_eml",
            "is_healthy",
        )
        sequence = ("checkbox", *fields)
