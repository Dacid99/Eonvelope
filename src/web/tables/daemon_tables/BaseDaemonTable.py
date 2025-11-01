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

"""test.web.tables.daemon_tables package containing daemon tables of the Emailkasten webapp."""

from django.utils.translation import gettext_lazy as _
from django_tables2 import Column, Table

from core.models import Daemon
from web.utils.columns import CheckboxColumn, IsHealthyColumn


class BaseDaemonTable(Table):
    checkbox = CheckboxColumn()
    uuid = Column(linkify=True)
    mailbox = Column(
        verbose_name=_("Mailbox"),
        linkify=lambda record: record.mailbox.get_absolute_url(),
        accessor="mailbox__name",
    )
    is_healthy = IsHealthyColumn()

    class Meta:
        model = Daemon
        fields = (
            "uuid",
            "mailbox",
            "fetching_criterion",
            "interval__period",
            "interval__every",
            "is_healthy",
        )
        sequence = ("checkbox", *fields)
