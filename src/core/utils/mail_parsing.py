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

"""Provides functions for parsing features from the maildata.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import email
import email.header
import email.utils
import logging
import re
from typing import TYPE_CHECKING

import imap_tools.imap_utf7
from django.utils import timezone


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
    joining_string: str = ",",
) -> str:
    """Shorthand to safely get a header from a :class:`email.message.EmailMessage`.

    Strips trailing whitespace from the header.

    Args:
        email_message: The message to get the header from.
        header_name: The name of the header field.
        joining_string: The string to join multiple headers with. Default to ',' which is safe for CharFields.

    Returns:
        The decoded header field as a string if found
        else "".
    """
    encoded_header = email_message.get_all(header_name)
    if not encoded_header:
        return ""
    return joining_string.join(
        [decode_header(header).strip() for header in encoded_header]
    )


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


def parse_mailbox_name(mailbox_data: bytes | str) -> str:
    """Parses the mailbox name as received by the `fetch_mailboxes` method in :mod:`core.utils.fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.
        The result must not be changed afterwards, otherwise opening the mailbox via this name is not possible!

    Args:
        mailbox_data: The mailbox name in bytes or as str as received from the mail server.

    Returns:
        The serverside name of the mailbox
    """
    mailbox_str = (
        imap_tools.imap_utf7.utf7_decode(mailbox_data)
        if isinstance(mailbox_data, bytes)
        else mailbox_data
    )
    match = re.search(
        r"\([\S ]*?\) [\S]+ (.+)", mailbox_str
    )  # regex taken from imap_tools.folder.MailBoxFolderManager.list
    if not match:
        return (
            mailbox_str.rsplit('"/"', maxsplit=1)[-1]
            .rsplit('"."', maxsplit=1)[-1]
            .strip()
        )
    return match.group(1)


def find_best_href_in_header(header: str) -> str:
    """Finds the best href in a header of hrefs.

    The href is selected via the logic: https > http > ...

    Returns:
        The best hyperref.
        The empty string if header is empty.
    """
    href_options = [part.strip().lstrip("<").rstrip(">") for part in header.split(",")]
    for option in href_options:
        if option.startswith("https"):
            return option
    for option in href_options:
        if option.startswith("http"):
            return option
    return href_options[0]


def is_x_spam(x_spam_header: str | None) -> bool:
    """Evaluates a x_spam header spam marker.

    Args:
        x_spam_header: The X-Spam-Flag header to evaluate.

    Returns:
        Whether the header marks its mail as spam.
    """
    return "YES" in str(x_spam_header)
