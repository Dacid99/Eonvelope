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

"""Module with the constant values for the :mod:`core` app."""
from __future__ import annotations

from typing import Final


class MailFetchingCriteria:
    """Namespace class for all implemented mail fetching criteria constants.

    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched.
    """

    RECENT: Final[str] = "RECENT"
    """Filter: str by "RECENT" flag."""

    UNSEEN: Final[str] = "UNSEEN"
    """Filter by "UNSEEN" flag."""

    ALL: Final[str] = "ALL"
    """Filter by "ALL" flag."""

    NEW: Final[str] = "NEW"
    """Filter by "NEW" flag."""

    OLD: Final[str] = "OLD"
    """Filter by "OLD" flag."""

    FLAGGED: Final[str] = "FLAGGED"
    """Filter by "FLAGGED" flag."""

    DRAFT: Final[str] = "DRAFT"
    """Filter by "DRAFT" flag."""

    ANSWERED: Final[str] = "ANSWERED"
    """Filter by "ANSWERED" flag."""

    DAILY: Final[str] = "DAILY"
    """Filter using "SENTSINCE" for mails sent the previous day or later."""

    WEEKLY: Final[str] = "WEEKLY"
    """Filter using "SENTSINCE" for mails sent the previous week (counting back from now) or later."""

    MONTHLY: Final[str] = "MONTHLY"
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks (counting back from now) or later."""

    ANNUALLY: Final[str] = "ANNUALLY"
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks (counting back from now) or later."""

    def __iter__(self):
        """Method to allow easier referencing of the members by listing.

        Note:
            value must come first in the listed tuples to match the format for field choices.
        """
        return iter(
            (value, attr)
            for attr, value in self.__class__.__dict__.items()
            if not attr.startswith("__")
        )

    def __getitem__(self, key):
        return getattr(self, key)


class MailFetchingProtocols:
    """Namespace class for all implemented mail protocols constants."""

    IMAP: Final[str] = "IMAP"
    """The IMAP4 protocol."""

    IMAP_SSL: Final[str] = "IMAP_SSL"
    """The IMAP4 protocol over SSL."""

    POP3: Final[str] = "POP3"
    """The POP3 protocol."""

    POP3_SSL: Final[str] = "POP3_SSL"
    """The POP3 protocol over SSL."""

    EXCHANGE: Final[str] = "EXCHANGE"
    """Microsofts Exchange protocol."""

    def __iter__(self):
        """Method to allow easier referencing of the members by listing.

        Note:
            value must come first in the listed tuples to match the format for field choices.
        """
        return iter(
            (value, attr)
            for attr, value in self.__class__.__dict__.items()
            if not attr.startswith("__")
        )

    def __getitem__(self, key):
        return getattr(self, key)


class HeaderFields:
    """Namespace class with all header fields that have their own column in the emails table.

    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.
    """

    MESSAGE_ID: Final[str] = "Message-ID"
    IN_REPLY_TO: Final[str] = "In-Reply-To"
    DATE: Final[str] = "Date"
    SUBJECT: Final[str] = "Subject"
    X_SPAM: Final[str] = "X-Spam-Flag"

    class MailingList:
        """Headers that are included in the mailinglists table."""

        ID: Final[str] = "List-Id"
        OWNER: Final[str] = "List-Owner"
        SUBSCRIBE: Final[str] = "List-Subscribe"
        UNSUBSCRIBE: Final[str] = "List-Unsubscribe"
        POST: Final[str] = "List-Post"
        HELP: Final[str] = "List-Help"
        ARCHIVE: Final[str] = "List-Archive"

    class Correspondents:
        """Headers that are treated as correspondents."""

        FROM: Final[str] = "From"
        TO: Final[str] = "To"
        CC: Final[str] = "Cc"
        BCC: Final[str] = "Bcc"
        SENDER: Final[str] = "Sender"
        REPLY_TO: Final[str] = "Reply-To"
        RESENT_FROM: Final[str] = "Resent-From"
        RESENT_TO: Final[str] = "Resent-To"
        RESENT_CC: Final[str] = "Resent-Cc"
        RESENT_BCC: Final[str] = "Resent-Bcc"
        RESENT_SENDER: Final[str] = "Resent-Sender"
        RESENT_REPLY_TO: Final[str] = "Resent-Reply-To"
        ENVELOPE_TO: Final[str] = "Envelope-To"
        DELIVERED_TO: Final[str] = "Delivered-To"
        RETURN_PATH: Final[str] = "Return-Path"
        RETURN_RECEIPT_TO: Final[str] = "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO: Final[str] = "Disposition-Notification-To"

        def __iter__(self):
            """Method to allow easier referencing of the members by listing.

            Note:
                value must come first in the listed tuples to match the format for field choices.
            """
            return iter(
                (value, attr)
                for attr, value in self.__class__.__dict__.items()
                if not attr.startswith("__")
            )

        def __getitem__(self, key):
            return getattr(self, key)
