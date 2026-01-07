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

"""core.utils.fetchers package containing the email fetcher classes for Eonvelope project."""

from .BaseFetcher import BaseFetcher
from .ExchangeFetcher import ExchangeFetcher
from .IMAP4_SSL_Fetcher import IMAP4_SSL_Fetcher
from .IMAP4Fetcher import IMAP4Fetcher
from .JMAPFetcher import JMAPFetcher
from .POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .POP3Fetcher import POP3Fetcher


__all__ = [
    "BaseFetcher",
    "ExchangeFetcher",
    "IMAP4Fetcher",
    "IMAP4_SSL_Fetcher",
    "JMAPFetcher",
    "POP3Fetcher",
    "POP3_SSL_Fetcher",
]
