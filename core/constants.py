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

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmailFetchingCriterionChoices(TextChoices):
    """Namespace class for all implemented mail fetching criteria constants.

    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched.
    """

    RECENT = "RECENT", _("All RECENT emails")
    """Filter by "RECENT" flag."""

    UNSEEN = "UNSEEN", _("All UNSEEN emails")
    """Filter by "UNSEEN" flag."""

    ALL = "ALL", _("All emails")
    """Filter by "ALL" flag."""

    NEW = "NEW", _("All RECENT and UNSEEN emails")
    """Filter by "NEW" flag."""

    OLD = "OLD", _("All emails that are not NEW")
    """Filter by "OLD" flag."""

    FLAGGED = "FLAGGED", _("FLAGGED emails")
    """Filter by "FLAGGED" flag."""

    DRAFT = "DRAFT", _("All email DRAFTs")
    """Filter by "DRAFT" flag."""

    UNDRAFT = "UNDRAFT", _("All emails that are not DRAFTs")
    """Filter by "UNDRAFT" flag."""

    ANSWERED = "ANSWERED", _("All ANSWERED emails")
    """Filter by "ANSWERED" flag."""

    UNANSWERED = "UNANSWERED", _("All UNANSWERED emails")
    """Filter by "UNANSWERED" flag."""

    DELETED = "DELETED", _("All DELETED emails")
    """Filter by "DELETED" flag."""

    UNDELETED = "UNDELETED", _("All UNDELETED emails")
    """Filter by "UNDELETED" flag."""

    DAILY = "DAILY", _("All emails received the last DAY")
    """Filter using "SENTSINCE" for mails sent the previous day."""

    WEEKLY = "WEEKLY", _("All emails received the last WEEK")
    """Filter using "SENTSINCE" for mails sent the previous week."""

    MONTHLY = "MONTHLY", _("All emails receiced the last MONTH")
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks."""

    ANNUALLY = "ANNUALLY", _("All emails received the last YEAR")
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks."""


class EmailProtocolChoices(TextChoices):
    """Namespace class for all implemented mail protocols constants."""

    IMAP = "IMAP", _("IMAP4")
    """The IMAP4 protocol"""

    IMAP4_SSL = "IMAP4_SSL", _("IMAP4 over SSL")
    """The IMAP4 protocol over SSL"""

    POP3 = "POP3", _("POP3")
    """The POP3 protocol"""

    POP3_SSL = "POP3_SSL", _("POP3 over SSL")
    """The POP3 protocol over SSL"""

    # EXCHANGE = "EXCHANGE", _("Microsoft Exchange")
    # """Microsofts Exchange protocol"""


class HeaderFields:
    """Namespace class with all header fields that have their own column in the emails table.

    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.
    """

    MESSAGE_ID: Final[str] = "Message-ID"
    IN_REPLY_TO: Final[str] = "In-Reply-To"
    DATE: Final[str] = "Date"
    SUBJECT: Final[str] = "Subject"
    X_SPAM: Final[str] = "X-Spam-Flag"
    CONTENT_ID: Final[str] = "Content-Id"

    class MailingList:
        """Headers that are included in the mailinglists table."""

        ID: Final[str] = "List-Id"
        OWNER: Final[str] = "List-Owner"
        SUBSCRIBE: Final[str] = "List-Subscribe"
        UNSUBSCRIBE: Final[str] = "List-Unsubscribe"
        POST: Final[str] = "List-Post"
        HELP: Final[str] = "List-Help"
        ARCHIVE: Final[str] = "List-Archive"

    class Correspondents(TextChoices):
        """Headers that are treated as correspondents.

        This class holds the choices for `core.models.EmailCorrespondents`.
        """

        FROM = "From", _("From")
        TO = "To", _("To")
        CC = "Cc", _("CC")
        BCC = "Bcc", _("BCC")
        SENDER = "Sender", _("Sender")
        REPLY_TO = "Reply-To", _("Reply-To")
        RESENT_FROM = "Resent-From", _("Resent-From")
        RESENT_TO = "Resent-To", _("Resent-To")
        RESENT_CC = "Resent-Cc", _("Resent-Cc")
        RESENT_BCC = "Resent-Bcc", _("Resent-Bcc")
        RESENT_SENDER = "Resent-Sender", _("Resent-Sender")
        RESENT_REPLY_TO = "Resent-Reply-To", _("Resent-Reply-To")
        ENVELOPE_TO = (
            "Envelope-To",
            "Envelope-To",
        )
        DELIVERED_TO = "Delivered-To", _("Delivered-To")
        RETURN_PATH = "Return-Path", _("Return-Path")
        RETURN_RECEIPT_TO = "Return-Receipt-To", _("Return-Receipt-To")
        DISPOSITION_NOTIFICATION_TO = (
            "Disposition-Notification-To",
            "Disposition-Notification-To",
        )


class SupportedEmailUploadFormats(TextChoices):
    """All fileformats that are supported for upload of emaildata."""

    EML = "eml", _(".eml")
    MBOX = "mbox", _(".mbox")
    MH = "mh", _(".mh")
    BABYL = "babyl", _(".babyl")
    MMDF = "mmdf", _(".mmdf")
    MAILDIR = "maildir", _(".maildir")
