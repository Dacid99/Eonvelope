# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
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

"""core.utils.fetchers package containing the email fetcher classes for Emailkasten project."""

from .BaseFetcher import BaseFetcher
from .IMAP4_SSL_Fetcher import IMAP4_SSL_Fetcher
from .IMAP4Fetcher import IMAP4Fetcher
from .POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .POP3Fetcher import POP3Fetcher


# from .ExchangeFetcher import ExchangeFetcher


__all__ = [
    "BaseFetcher",
    "IMAP4Fetcher",
    "IMAP4_SSL_Fetcher",
    "POP3Fetcher",
    "POP3_SSL_Fetcher",
    # "ExchangeFetcher"
]
