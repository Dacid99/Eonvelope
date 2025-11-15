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

""":mod:`web.tables package` containing all tables for the Eonvelope webapp."""

from .account_tables import BaseAccountTable
from .attachment_tables import BaseAttachmentTable
from .correspondent_tables import BaseCorrespondentTable
from .daemon_tables import BaseDaemonTable
from .email_tables import BaseEmailTable
from .emailcorrespondent_tables import BaseCorrespondentEmailTable
from .mailbox_tables import BaseMailboxTable


__all__ = [
    "BaseAccountTable",
    "BaseAttachmentTable",
    "BaseCorrespondentEmailTable",
    "BaseCorrespondentTable",
    "BaseDaemonTable",
    "BaseEmailTable",
    "BaseMailboxTable",
]
