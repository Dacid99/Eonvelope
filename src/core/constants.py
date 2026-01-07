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

"""Module with the constant values for the :mod:`core` app."""

from __future__ import annotations

import mailbox
from typing import Final

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


INTERNAL_DATE_FORMAT = "%Y-%m-%d"


class EmailFetchingCriterionChoices(TextChoices):
    """Namespace class for all implemented mail fetching criteria constants.

    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always referring to full days.
    """

    DAILY = "DAILY", _("All emails received the last DAY")
    """Filter using "SENTSINCE" for mails sent the previous day."""

    WEEKLY = "WEEKLY", _("All emails received the last WEEK")
    """Filter using "SENTSINCE" for mails sent the previous week."""

    MONTHLY = "MONTHLY", _("All emails received the last MONTH")
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

    UNFLAGGED = "UNFLAGGED", _("All emails that are not FLAGGED")
    """Filter by "UNFLAGGED" flag."""

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

    # all filters with arg
    KEYWORD = "KEYWORD {}", _("All emails with the given KEYWORD")
    """Filter by "KEYWORD". Must be formatted."""

    UNKEYWORD = "UNKEYWORD {}", _("All emails without the given KEYWORD")
    """Filter by "UNKEYWORD". Must be formatted."""

    LARGER = "LARGER {}", _("All emails LARGER than the given size")
    """Filter by "LARGER". Must be formatted."""

    SMALLER = "SMALLER {}", _("All emails SMALLER than the given size")
    """Filter by "SMALLER". Must be formatted."""

    SUBJECT = "SUBJECT {}", _("All emails with SUBJECT containing the given text")
    """Filter by "SUBJECT" content. Must be formatted."""

    BODY = "BODY {}", _("All emails with BODY containing the given text")
    """Filter by "BODY" content. Must be formatted."""

    FROM = "FROM {}", _("All emails sent FROM the given address")
    """Filter by "FROM" header. Must be formatted."""

    SENTSINCE = "SENTSINCE {}", _("All emails SENT SINCE the given date")
    """Filter by "SENTSINCE" time. Must be formatted."""


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
    """Microsoft's Exchange protocol"""

    JMAP = "JMAP", _("JMAP")
    """The JMAP protocol"""


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


PROTOCOLS_SUPPORTING_RESTORE = (
    EmailProtocolChoices.IMAP,
    EmailProtocolChoices.IMAP4_SSL,
    EmailProtocolChoices.EXCHANGE,
    EmailProtocolChoices.JMAP,
)
"""All protocols supporting restoring of emails."""

HTML_SUPPORTED_AUDIO_TYPE = (
    "ogg",
    "wav",
    "mpeg",
    "aac",
)
"""All audio types supported by html elements."""

HTML_SUPPORTED_VIDEO_TYPES = (
    "ogg",
    "mp4",
    "mpeg",
    "webm",
    "avi",
)
"""All video types supported by html elements."""

PAPERLESS_SUPPORTED_IMAGE_TYPES = (
    "png",
    "jpeg",
    "pjpeg",
    "tiff",
    "x-tiff",
    "gif",
    "webp",
)
"""All image types supported by Paperless."""

PAPERLESS_TIKA_SUPPORTED_MIMETYPES = (
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
    SupportedEmailUploadFormats.MBOX: mailbox.mbox,
    SupportedEmailUploadFormats.BABYL: mailbox.Babyl,
    SupportedEmailUploadFormats.MMDF: mailbox.MMDF,
    SupportedEmailUploadFormats.MAILDIR: mailbox.Maildir,
    SupportedEmailUploadFormats.MH: mailbox.MH,
}
"""Mapping of supported file formats to their parser classes."""

ICALENDAR_TEMPLATE = """<div class="row g-0 overflow-y-scroll">
                            <div class="d-flex flex-column align-items-start">
                                {% for dtstart, dtend, summary, location in icalendar_readout %}
                                    <div class="card shadow-sm">
                                        <div class="card-body d-flex align-items-center justify-content-center gap-3">
                                            <div class="text-center border rounded p-2 fw-bold">
                                                <div class="text-bg-success px-2 py-1 fs-5">
                                                    {{ dtstart | date:"M" }}
                                                </div>
                                                <div class="fs-2">
                                                    {{ dtstart | date:"j"}}
                                                </div>
                                                <div class="text-muted">
                                                    {{ dtstart |date:"Y" }}
                                                </div>
                                            </div>
                                            <div class="flex-grow">
                                                <h5 class="card-title">{{ summary }}</h5>
                                                <p class="card-text text-muted d-flex flex-column">
                                                    <span>{{ dtstart | time }}</span>
                                                    <span class="mx-1">-</span>
                                                    {% if dtend.date != dtstart.date %}<span class="fw-bold me-1">{{dtend |date }}</span>{% endif %}
                                                    <span>{{ dtend | time }}</span>
                                                </p>
                                                <p class="card-text text-muted">
                                                    {{ location }}
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                {% endfor %}
                            </div>
                        </div>"""


VCARD_TEMPLATE = """{% load i18n %}

                    <div class="row g-0 overflow-y-scroll">
                        <div class="d-flex flex-column align-items-start">
                            {% for full_name, photo_data, email, address, tel in vcard_readout %}
                                <div class="card shadow-sm">
                                    <div class="card-body">
                                        <div class="d-flex justify-content-between">
                                        <h5 class="card-title m-1">
                                            {{ fname }}
                                        </h5>
                                            {% if photo_data %}
                                                <img class="img-thumbnail"
                                                        src="data:image/jpeg;base64,{{ photo_data }}"
                                                        alt={% translate "Contact picture" %}
                                                        width="32px">
                                            {% else %}
                                                <i class="fa-regular fa-id-badge fa-2xl" ><span class="visually-hidden">{% translate "Contact picture placeholder" %}</span></i>
                                            {% endif %}
                                        </div>
                                        <div class="card-text text-muted d-flex flex-column">
                                            {% if address %}
                                                <span>{% translate "Address" %}: {{ address }}</span>
                                            {% endif %}
                                            {% if email %}
                                                <span>{% translate "Email" %}: <a href="mailto:{{ email }}" class="link-info link-offset-2 link-underline link-underline-opacity-0 link-underline-opacity-75-hover">{{ email }}</span>
                                            {% endif %}
                                            {% if tel %}
                                                <span>{% translate "Tel" %}: <a href="tel:{{ tel }}" class="link-success link-offset-2 link-underline link-underline-opacity-0 link-underline-opacity-75-hover">{{ tel }}</span>
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                            {% endfor %}
                        </div>
                    </div>"""
