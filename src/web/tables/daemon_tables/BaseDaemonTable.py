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

"""Module with the :class:`web.tables.BaseDaemonTable` table class."""

from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import Daemon
from web.utils.columns import CheckboxColumn, IsHealthyColumn


class BaseDaemonTable(Table):
    """Table class for :class:`core.models.Daemon.Daemon`."""

    checkbox = CheckboxColumn()
    uuid = Column(linkify=True)
    mailbox = Column(
        verbose_name=_("Mailbox"),
        linkify=lambda record: record.mailbox.get_absolute_url(),
        accessor="mailbox__name",
    )
    is_healthy = IsHealthyColumn()

    class Meta:
        """Metadata class for the table."""

        model = Daemon
        fields = (
            "uuid",
            "mailbox",
            "fetching_criterion",
            "interval__every",
            "interval__period",
            "is_healthy",
        )
        sequence = ("checkbox", *fields)
