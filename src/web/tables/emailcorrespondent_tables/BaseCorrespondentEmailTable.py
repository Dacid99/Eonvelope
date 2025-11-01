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

"""Module with the :class:`web.tables.BaseCorrespondentEmailTable` table class."""

from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import EmailCorrespondent
from web.utils.columns import CheckboxColumn, IsFavoriteColumn


class BaseCorrespondentEmailTable(Table):
    """Table class for :class:`core.models.CorrespondentEmail.CorrespondentEmail`."""

    checkbox = CheckboxColumn()
    email__is_favorite = IsFavoriteColumn()
    email__subject = Column(
        linkify=lambda record: record.email.get_absolute_url(),
    )
    email__mailbox = Column(
        verbose_name=_("Mailbox"),
        linkify=lambda record: record.email.mailbox.get_absolute_url(),
        accessor="mailbox__name",
    )
    email__mailbox__account = Column(
        verbose_name=_("Account"),
        linkify=lambda record: record.email.mailbox.account.get_absolute_url(),
        accessor="mailbox__account__mail_address",
    )

    class Meta:
        """Metadata class for the table."""

        model = EmailCorrespondent
        fields = (
            "mention",
            "email__is_favorite",
            "email__subject",
            "email__datetime",
            "email__mailbox",
            "email__mailbox__account",
            "email__x_spam",
            "email__datasize",
        )
        sequence = ("checkbox", *fields)

    def render_checkbox(self, record: Model, column: CheckboxColumn):
        """Fixes the rendering of checkbox to use the email as record."""
        return column.render(record=record.email)

    def render_email__is_favorite(self, record: Model, column: IsFavoriteColumn):
        """Fixes the rendering of the favorite badge to use the email as record."""
        return column.render(record=record.email)
