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

"""core.models package containing models for the Emailkasten database."""

from .Account import Account
from .Attachment import Attachment
from .Correspondent import Correspondent
from .Daemon import Daemon
from .Email import Email
from .EmailCorrespondent import EmailCorrespondent
from .Mailbox import Mailbox


__all__ = [
    "Account",
    "Attachment",
    "Correspondent",
    "Daemon",
    "Email",
    "EmailCorrespondent",
    "Mailbox",
]
