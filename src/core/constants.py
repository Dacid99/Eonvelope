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

"""Module with the constant values for the :mod:`core` app."""

from __future__ import annotations

import mailbox
from typing import Final

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class EmailFetchingCriterionChoices(TextChoices):
    """Namespace class for all implemented mail fetching criteria constants.

    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always referring to full days.
    POP does not support queries at all, so everything will be fetched.
    """

    DAILY = "DAILY", _("All emails received the last DAY")
    """Filter using "SENTSINCE" for mails sent the previous day."""

    WEEKLY = "WEEKLY", _("All emails received the last WEEK")
    """Filter using "SENTSINCE" for mails sent the previous week."""

    MONTHLY = "MONTHLY", _("All emails receiced the last MONTH")
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks."""

    ANNUALLY = "ANNUALLY", _("All emails received the last YEAR")
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks."""

    RECENT = "RECENT", _("All RECENT emails")
    """Filter by "RECENT" flag."""

    UNSEEN = "UNSEEN", _("All UNSEEN emails")
    """Filter by "UNSEEN" flag."""

    SEEN = "SEEN", _("All SEEN emails")
    """Filter by "SEEN" flag."""

    ALL = "ALL", _("All emails")
    """Filter by "ALL" flag."""

    NEW = "NEW", _("All RECENT and UNSEEN emails")
    """Filter by "NEW" flag."""

    OLD = "OLD", _("All emails that are not RECENT")
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


class EmailProtocolChoices(TextChoices):
    """Namespace class for all implemented mail protocols constants."""

    IMAP4_SSL = "IMAP4_SSL", _("IMAP4")
    """The IMAP4 protocol over SSL"""

    IMAP = "IMAP", _("IMAP4 (unencrypted)")
    """The IMAP4 protocol"""

    POP3_SSL = "POP3_SSL", _("POP3")
    """The POP3 protocol over SSL"""

    POP3 = "POP3", _("POP3 (unencrypted)")
    """The POP3 protocol"""

    EXCHANGE = "EXCHANGE", _("Microsoft Exchange")
    """Microsofts Exchange protocol"""


class HeaderFields:
    """Namespace class with all header fields that have their own column in the emails table.

    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.

    All header field names are lowercase and the lookups case-insensitive to avoid issues with different spellings.
    """

    MESSAGE_ID: Final[str] = "message-id"
    IN_REPLY_TO: Final[str] = "in-reply-to"
    REFERENCES: Final[str] = "references"
    DATE: Final[str] = "date"
    SUBJECT: Final[str] = "subject"
    X_SPAM: Final[str] = "x-spam-flag"
    CONTENT_ID: Final[str] = "content-id"

    class MailingList:
        """Headers that are included in the mailinglists table."""

        ID: Final[str] = "list-id"
        OWNER: Final[str] = "list-owner"
        SUBSCRIBE: Final[str] = "list-subscribe"
        UNSUBSCRIBE: Final[str] = "list-unsubscribe"
        UNSUBSCRIBE_POST: Final[str] = "list-unsubscribe-post"
        POST: Final[str] = "list-post"
        HELP: Final[str] = "list-help"
        ARCHIVE: Final[str] = "list-archive"

    class Correspondents(TextChoices):
        """Headers that are treated as correspondents.

        This class holds the choices for `core.models.EmailCorrespondents`.
        """

        FROM = "from", _("From")
        TO = "to", _("To")
        CC = "cc", _("CC")
        BCC = "bcc", _("BCC")
        SENDER = "sender", _("Sender")
        REPLY_TO = "reply-To", _("Reply-To")
        RESENT_FROM = "resent-from", _("Resent-From")
        RESENT_TO = "resent-to", _("Resent-To")
        RESENT_CC = "resent-cc", _("Resent-Cc")
        RESENT_BCC = "resent-bcc", _("Resent-Bcc")
        RESENT_SENDER = "resent-sender", _("Resent-Sender")
        RESENT_REPLY_TO = "resent-reply-to", _("Resent-Reply-To")
        ENVELOPE_TO = (
            "envelope-to",
            _("Envelope-To"),
        )
        DELIVERED_TO = "delivered-to", _("Delivered-To")
        RETURN_PATH = "return-path", _("Return-Path")
        RETURN_RECEIPT_TO = "return-receipt-to", _("Return-Receipt-To")
        DISPOSITION_NOTIFICATION_TO = (
            "disposition-notification-to",
            _("Disposition-Notification-To"),
        )


class SupportedEmailDownloadFormats(TextChoices):
    """All fileformats that are available for download of emaildata.

    The file extension is taken from the value as value.split("[]").
    """

    ZIP_EML = "zip[eml]", _(".zip with .eml files inside")
    MBOX = "mbox", _(".mbox")
    BABYL = "babyl", _(".babyl")
    MMDF = "mmdf", _(".mmdf")
    MH = "zip[mh]", _(".zip with mh mailbox inside")
    MAILDIR = "zip[maildir]", _(".zip with maildir mailbox inside")


class SupportedEmailUploadFormats(TextChoices):
    """All fileformats that are supported for upload of emaildata."""

    EML = "eml", _(".eml")
    ZIP_EML = "zip[eml]", _(".zip with .eml files inside")
    MBOX = "mbox", _(".mbox")
    BABYL = "babyl", _(".babyl")
    MMDF = "mmdf", _(".mmdf")
    MH = "zip[mh]", _(".zip with mh mailbox inside")
    MAILDIR = "zip[maildir]", _(".zip with maildir mailbox inside")


PROTOCOLS_SUPPORTING_RESTORE: tuple[str] = (
    EmailProtocolChoices.IMAP,
    EmailProtocolChoices.IMAP4_SSL,
    EmailProtocolChoices.EXCHANGE,
)
"""All protocols supporting restoring of emails."""

HTML_SUPPORTED_AUDIO_TYPE: tuple[str] = (
    "ogg",
    "wav",
    "mpeg",
    "aac",
)
"""All audio types supported by html elements."""

HTML_SUPPORTED_VIDEO_TYPES: tuple[str] = (
    "ogg",
    "mp4",
    "mpeg",
    "webm",
    "avi",
)
"""All video types supported by html elements."""

PAPERLESS_SUPPORTED_IMAGE_TYPES: tuple[str] = (
    "png",
    "jpeg",
    "pjpeg",
    "tiff",
    "x-tiff",
    "gif",
    "webp",
)
"""All image types supported by Paperless."""

PAPERLESS_TIKA_SUPPORTED_MIMETYPES: tuple[str] = (
    "msword",
    "vnd.openxmlformats-officedocument.wordprocessingml.document",
    "vnd.oasis.opendocument.text",
    "powerpoint",
    "mspowerpoint",
    "vnd.ms-powerpoint",
    "vnd.openxmlformats-officedocument.presentationml.presentation",
    "vnd.oasis.opendocument.presentation",
    "excel",
    "msexcel",
    "x-excel",
    "x-msexcel",
    "vnd.ms-excel",
    "vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "vnd.oasis.opendocument.spreadsheet",
)
"""All application types supported by Paperless Tika."""

IMMICH_SUPPORTED_APPLICATION_TYPES = ("photoshop", "x-matroska", "mp4")
"""All application types supported by Immich."""

IMMICH_SUPPORTED_IMAGE_TYPES = (
    "avif",
    "bmp",
    "x-bmp",
    "x-ms-bmp",
    "gif",
    "heic",
    "heif",
    "jp2",
    "jpeg",
    "pjpeg",
    "jxl",
    "png",
    "vnd.adobe.photoshop",
    "x-psd",
    "raw",
    "x-raw-panasonic",
    "x-panasonic-raw",
    "x-panasonic-raw2",
    "x-panasonic-rw",
    "x-panasonic-rw2",
    "svg+xml",
    "tiff",
    "x-tiff",
    "webp",
)
"""All image types supported by Immich."""

IMMICH_SUPPORTED_VIDEO_TYPES = (
    "3gpp",
    "x-msvideo",
    "x-flv",
    "x-m4v",
    "matroska",
    "x-matroska",
    "matroska-3d",
    "mp2t",
    "mp4",
    "mpeg",
    "quicktime",
    "webm",
    "x-ms-wmv",
)
"""All video types supported by Immich."""

file_format_parsers: Final[
    dict[
        str,
        type[
            mailbox.mbox | mailbox.Babyl | mailbox.MMDF | mailbox.Maildir | mailbox.MH
        ],
    ]
] = {
    SupportedEmailUploadFormats.MBOX.value: mailbox.mbox,
    SupportedEmailUploadFormats.BABYL.value: mailbox.Babyl,
    SupportedEmailUploadFormats.MMDF.value: mailbox.MMDF,
    SupportedEmailUploadFormats.MAILDIR.value: mailbox.Maildir,
    SupportedEmailUploadFormats.MH.value: mailbox.MH,
}
"""Mapping of supported file formats to their parser classes."""
