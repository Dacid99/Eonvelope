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

"""Module with signals for the Emailkasten database models."""

from .delete_Attachment import post_delete_attachment
from .delete_Email import post_delete_email
from .save_Account import post_save_account_is_healthy
from .save_Daemon import post_save_daemon_is_healthy
from .save_Mailbox import post_save_mailbox_is_healthy


__all__ = [
    "post_delete_attachment",
    "post_delete_email",
    "post_save_account_is_healthy",
    "post_save_daemon_is_healthy",
    "post_save_mailbox_is_healthy",
]
