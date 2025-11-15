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

"""Exceptions for errors during operations on mailservers."""

from typing import Any

from django.utils.translation import gettext_lazy as _


class FetcherError(Exception):
    """Base exception class for errors during operations on mailservers."""


class MailAccountError(FetcherError):
    """Exception for errors concerning the mail account."""

    def __init__(self, error: Exception, command_name: str = _("interaction")) -> None:
        """Extended for consistent message formatting."""
        super().__init__(
            _(
                "A %(error_class_name)s: %(error)s occurred during %(command_name)s on account!"
            )
            % {
                "error_class_name": error.__class__.__name__,
                "error": error,
                "command_name": command_name,
            }
        )


class MailboxError(FetcherError):
    """Exception for errors concerning the mailbox."""

    def __init__(self, error: Exception, command_name: str = _("interaction")) -> None:
        """Extended for consistent message formatting."""
        super().__init__(
            _(
                "A %(error_class_name)s: %(error)s occurred during %(command_name)s on mailbox!"
            )
            % {
                "error_class_name": error.__class__.__name__,
                "error": error,
                "command_name": command_name,
            }
        )


class BadServerResponseError(Exception):
    """Exception for unexpected server responses."""

    def __init__(self, response: Any = "") -> None:
        """Extended for consistent message formatting."""
        super().__init__(_("Server responded %(response)s!") % {"response": response})
