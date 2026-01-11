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

import contextlib
import email.header
import email.utils
import logging
import re
from base64 import b64encode
from datetime import datetime, time
from typing import TYPE_CHECKING, TextIO

import imap_tools.imap_utf7
import vobject
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from core.constants import MailboxTypeChoices


if TYPE_CHECKING:
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


def parse_datetime_header(date_header: str | None) -> datetime:
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


def parse_IMAP_mailbox_data(mailbox_data: bytes | str) -> tuple[str, str]:
    """Parses the mailbox name as received in :mod:`core.utils.fetchers.IMAP4Fetcher`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.
        The result must not be changed afterwards, otherwise opening the mailbox via this name is not possible!

    Args:
        mailbox_data: The mailbox data in bytes or as str as received from the mail server.

    Returns:
        The serverside name of the mailbox.
    """
    mailbox_str = (
        imap_tools.imap_utf7.utf7_decode(mailbox_data)
        if isinstance(mailbox_data, bytes)
        else mailbox_data
    )
    match = re.search(
        r"\(([\S ]*?)\) [\S]+ (.+)", mailbox_str
    )  # regex adapted from imap_tools.folder.MailBoxFolderManager.list
    return match.group(1), match.group(2)


def parse_mailbox_type(mailbox_type_name: str) -> str:
    """Maps the mailbox type names from the various protocols to the choice enum."""
    # Ordered: IMAP | Exchange | JMAP, shortened if there are identities
    mailbox_type_name = mailbox_type_name.lower()
    if "inbox" in mailbox_type_name:
        return MailboxTypeChoices.INBOX
    if "outbox" in mailbox_type_name:
        return MailboxTypeChoices.OUTBOX
    if "sent" in mailbox_type_name:
        return MailboxTypeChoices.SENT
    if "drafts" in mailbox_type_name:
        return MailboxTypeChoices.DRAFTS
    if "junk" in mailbox_type_name:
        return MailboxTypeChoices.JUNK
    if "trash" in mailbox_type_name or "deleted" in mailbox_type_name:
        return MailboxTypeChoices.TRASH
    return MailboxTypeChoices.CUSTOM


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


def is_x_spam(x_spam_header: str | None) -> bool | None:
    """Evaluates a x_spam header spam marker.

    Args:
        x_spam_header: The X-Spam-Flag header to evaluate.

    Returns:
        Whether the header marks its mail as spam.
        None if there is no header and thus no statement about the spam property.
    """
    return ("YES" in x_spam_header) if x_spam_header else None


def make_icalendar_readout(
    icalendar_file: TextIO,
) -> list[tuple[datetime, datetime, str, str]]:
    """Parses the main features of a icalendar file into a list.

    References:
        https://www.rfc-editor.org/rfc/rfc5545.html#page-52

    Args:
        icalendar_file: The icalendar file to parse.

    Returns:
        A list with the calendar events main features in tuples.
    """
    calendar_readout = []
    with contextlib.suppress(vobject.base.VObjectError):
        for calendar in vobject.readComponents(icalendar_file):
            for event in calendar.vevent_list:
                if "dtstart" not in event.contents:
                    continue
                dtstart = event.dtstart.value
                dtstart = (
                    dtstart.astimezone(get_current_timezone())
                    if isinstance(dtstart, datetime)
                    else datetime.combine(
                        dtstart,
                        time.min,
                        tzinfo=get_current_timezone(),
                    )
                )
                if "dtend" in event.contents:
                    dtend = event.dtend.value
                    dtend = (
                        dtend.astimezone(get_current_timezone())
                        if isinstance(dtend, datetime)
                        else datetime.combine(
                            dtend,
                            time.min,
                            tzinfo=get_current_timezone(),
                        )
                    )
                elif "duration" in event.contents:
                    dtend = dtstart + event.duration.value
                else:
                    dtend = datetime.combine(
                        dtstart.date(),
                        time.max,
                        dtstart.tzinfo,
                    )
                summary = (
                    str(event.summary.value).strip()
                    if "summary" in event.contents
                    else ""
                )
                location = (
                    str(event.location.value).strip()
                    if "location" in event.contents
                    else ""
                )
                calendar_readout.append((dtstart, dtend, summary, location))
    return calendar_readout


def make_vcard_readout(
    vcard_file: TextIO,
) -> list[tuple[datetime, datetime, str, str]]:
    """Parses the main features of a vcard file into a list.

    References:
        https://www.rfc-editor.org/rfc/rfc5545.html#page-52

    Args:
        vcard_file: The vcard file to parse.

    Returns:
        A list with the cards main features in tuples.
    """
    calendar_readout = []
    with contextlib.suppress(vobject.base.VObjectError):
        for contact in vobject.readComponents(vcard_file):
            full_name = contact.fn.value if "fn" in contact.contents else ""
            photo_data = (
                b64encode(contact.photo.value).decode(
                    "utf-8"
                )  # to get a string for use in img src
                if "photo" in contact.contents
                else ""
            )
            contact_email = (
                str(contact.email.value).strip() if "email" in contact.contents else ""
            )
            contact_address = (
                str(contact.adr.value).strip() if "adr" in contact.contents else ""
            )
            contact_tel = (
                str(contact.tel.value).strip() if "tel" in contact.contents else ""
            )
            calendar_readout.append(
                (full_name, photo_data, contact_email, contact_address, contact_tel)
            )
    return calendar_readout
