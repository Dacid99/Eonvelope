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

"""Provides functions for parsing features from the maildata.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import email
import email.header
import email.utils
import logging
from base64 import b64encode
from typing import TYPE_CHECKING

import imap_tools.imap_utf7
from django.utils import timezone
from html_sanitizer.django import get_sanitizer

from Emailkasten.utils.workarounds import get_config


if TYPE_CHECKING:
    import datetime
    from email.header import Header
    from email.message import EmailMessage

logger = logging.getLogger(__name__)


def decode_header(header: Header | str) -> str:
    """Decodes an email header field.

    Note:
        Uses :func:`email.header.decode_header`.

    Args:
        header: The mail header to decode.

    Returns:
        The decoded mail header.
    """
    decoded_fragments = email.header.decode_header(header)
    decoded_string = ""
    for fragment, charset in decoded_fragments:
        decoded_string += (
            fragment.decode(charset if charset else "utf-8", errors="replace")
            if isinstance(fragment, bytes)
            else fragment
        )

    return decoded_string


def get_header(
    email_message: EmailMessage,
    header_name: str,
    joining_string: str = ", ",
) -> str | None:
    """Shorthand to safely get a header from a :class:`email.message.EmailMessage`.

    Args:
        email_message: The message to get the header from.
        header_name: The name of the header field.
        joining_string: The string to join multiple headers with. Default to ', ' which is safe for CharFields.

    Returns:
        The decoded header field as a string if found
        else "".
    """
    encoded_header = email_message.get_all(header_name)
    if not encoded_header:
        return ""
    return joining_string.join([decode_header(header) for header in encoded_header])


def parse_datetime_header(date_header: str | None) -> datetime.datetime:
    """Parses the date header into a datetime object.

    If an error occurs uses the current time as fallback.

    Note:
        Uses :func:`email.utils.parsedate_to_datetime`
        and :func:`django.utils.timezone.now`.

    Args:
        date_header: The datetime header to parse.

    Returns:
        The datetime version of the header.
        The current time in case of an invalid date header.
    """
    if not date_header:
        logger.warning(
            "No Date header found in mail, resorting to current time!",
        )
        return timezone.now()
    try:
        parsed_datetime = email.utils.parsedate_to_datetime(date_header)
    except ValueError:
        logger.warning(
            "No parseable Date header found in mail, resorting to current time!",
            exc_info=True,
        )
        return timezone.now()
    return parsed_datetime


def get_bodytexts(email_message: EmailMessage) -> dict[str, str]:
    """Parses the various bodytexts from a :class:`email.message.EmailMessage`.

    Args:
        email_message: The message to parse the bodytexts from.

    Returns:
        A dict containing the bodytexts with their contenttypes as keys.
    """
    bodytexts = {}
    for part in email_message.walk():
        content_maintype = part.get_content_maintype()
        content_subtype = part.get_content_subtype()
        if content_maintype == "text" and not part.get_content_disposition():
            bodytexts[content_subtype] = part.get_content()
    return bodytexts


def parse_mailbox_name(mailbox_bytes: bytes) -> str:
    """Parses the mailbox name as received by the `fetch_mailboxes` method in :mod:`core.utils.fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.
        The result must not be changed afterwards, otherwise opening the mailbox via this name is not possible!
    Args:
        mailbox_bytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The serverside name of the mailbox
    """
    return (
        imap_tools.imap_utf7.utf7_decode(mailbox_bytes)
        .rsplit('"/"', maxsplit=1)[-1]
        .strip()
    )


def message2html(email_message: EmailMessage) -> str:
    """Creates a html presentation of an email.

    Args:
        email_bytes: The data of the mail to be converted.

    Todo:
        ignoreplaintext mechanism may ignore too broadly

    Returns:
        The html representation of the email.
    """
    ignore_plain_text = False

    html_wrapper = get_config("HTML_WRAPPER")
    html = ""
    cid_content: dict[str, EmailMessage] = {}
    attachments_footer = ""
    for part in email_message.walk():
        if part.get_content_subtype() == "alternative":
            ignore_plain_text = True
            continue
        content_maintype = part.get_content_maintype()
        content_subtype = part.get_content_subtype()
        content_disposition = part.get_content_disposition()
        # The order of the conditions is crucial
        if content_maintype == "text":
            if content_subtype == "html":
                charset = part.get_content_charset("utf-8")
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    html += payload.decode(charset, errors="replace")
                else:
                    logger.debug(
                        "UNEXPECTED: %s/%s part payload was of type %s.",
                        content_maintype,
                        content_subtype,
                        type(payload),
                    )
            elif not ignore_plain_text:
                charset = part.get_content_charset("utf-8")
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    text = payload.decode(charset, errors="replace")
                    html += html_wrapper % text
                else:
                    logger.debug(
                        "UNEXPECTED: %s/%s part payload was of type %s.",
                        content_maintype,
                        content_subtype,
                        type(payload),
                    )
        elif content_maintype == "image":
            if cid := part.get("Content-ID", None):
                cid_content[cid.strip("<>")] = part

        elif content_disposition == "inline":
            if cid := part.get("Content-ID", None):
                cid_content[cid.strip("<>")] = part
            else:
                file_name = (
                    part.get_filename() or f"{hash(part)}.{part.get_content_subtype()}"
                )
                attachments_footer += "<li>" + file_name + "</li>"

        elif content_disposition == "attachment":
            file_name = (
                part.get_filename() or f"{hash(part)}.{part.get_content_subtype()}"
            )
            attachments_footer += "<li>" + file_name + "</li>"

    for cid, part in cid_content.items():
        content_type = part.get_content_type()
        part_bytes = part.get_payload(decode=True)
        if isinstance(part_bytes, bytes):
            base64part = b64encode(part_bytes).decode("utf-8")
            html = html.replace(
                f'src="cid:{cid}"', f'src="data:{content_type};base64,{base64part}"'
            )
        else:
            logger.debug(
                "UNEXPECTED: %s part payload was of type %s.",
                content_type,
                type(part_bytes),
            )
    if attachments_footer:
        html = html.replace(
            "</html>",
            f"<p><hr><p><b>Attached Files:</b><p><ul>{attachments_footer}</ul></html>",
        )
    return get_sanitizer().sanitize(html)  # type: ignore[no-any-return]  # always returns a str, mypy cant read html_sanitizer


def is_x_spam(x_spam_header: str | None) -> bool:
    """Evaluates a x_spam header spam marker.

    Args:
        x_spam_header: The X-Spam-Flag header to evaluate.

    Returns:
        Whether the header marks its mail as spam.
    """
    return "YES" in str(x_spam_header)
