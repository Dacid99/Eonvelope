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

"""Module with the :class:`web.tables.BasDaemonTable` table class."""

from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import Email
from web.utils.columns import CheckboxColumn, IsFavoriteColumn


class BaseEmailTable(Table):
    """Table class for :class:`core.models.Email.Email`."""

    checkbox = CheckboxColumn()
    is_favorite = IsFavoriteColumn()
    subject = Column(linkify=True)
    mailbox = Column(
        verbose_name=_("Mailbox"),
        linkify=lambda record: record.mailbox.get_absolute_url(),
        accessor="mailbox__name",
    )
    mailbox__account = Column(
        verbose_name=_("Account"),
        linkify=lambda record: record.mailbox.account.get_absolute_url(),
        accessor="mailbox__account__mail_address",
    )

    class Meta:
        """Metadata class for the table."""

        model = Email
        fields = (
            "is_favorite",
            "subject",
            "datetime",
            "mailbox",
            "mailbox__account",
            "x_spam",
            "datasize",
        )
        sequence = ("checkbox", *fields)

    def render_datasize(self, value: int) -> str:
        """Renders the datasize value by adding the bytes unit.

        Args:
            value: The datasize value

        Returns:
            The string shown for datasize in the table.
        """
        return str(value) + " " + _("bytes")
