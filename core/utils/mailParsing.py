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
Functions starting with _ are helpers and are used only within the scope of this module.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import datetime
import email
import email.header
import email.message
import email.utils
import logging
from email.utils import parseaddr
from typing import TYPE_CHECKING

import email_validator
import imap_tools.imap_utf7
from django.utils import timezone

from Emailkasten.utils import get_config

if TYPE_CHECKING:
    from email.header import Header
    from email.message import EmailMessage
    from typing import Callable

logger = logging.getLogger(__name__)


def decodeHeader(header: Header | str) -> str:
    """Decodes an email header field.

    Note:
        Uses :func:`email.header.decode_header`.

    Args:
        header: The mail header to decode.

    Returns:
        The decoded mail header.
    """
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if not charset:
            decodedString += (
                fragment.decode(errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )
        else:
            decodedString += (
                fragment.decode(charset, errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )

    return decodedString


def getHeader(
    emailMessage: EmailMessage,
    headerName: str,
    joiningString: str = ", ",
    fallbackCallable: Callable[[], str | None] = lambda: None,
) -> str | None:
    """Shorthand to safely get a header from a :class:`email.message.EmailMessage`.

    Args:
        emailMessage: The message to get the header from.
        headerName: The name of the header field.
        joiningString: The string to join multiple headers with. Default to ', ' which is safe for CharFields.
        fallbackCallable: A callable that provides a fallback if the field is not found.
            Is only executed if required. Defaults to `lambda: None`.

    Returns:
        The decoded header field as a string if found
        else the return of the :attr:`fallbackCallable`.
    """
    encoded_header = emailMessage.get_all(headerName)
    if not encoded_header:
        return fallbackCallable()
    return joiningString.join([decodeHeader(header) for header in encoded_header])


def parseDatetimeHeader(dateHeader: str | None) -> datetime.datetime:
    """Parses the date header into a datetime object.
    If an error occurs uses the current time as fallback.

    Note:
        Uses :func:`email.utils.parsedate_to_datetime`
        and :func:`django.utils.timezone.now`.

    Args:
        dateHeader: The datetime header to parse.

    Returns:
        The datetime version of the header.
        The current time in case of an invalid date header.
    """
    try:
        parsedDatetime = email.utils.parsedate_to_datetime(dateHeader)
    except ValueError:
        logger.warning(
            "No parseable Date header found in mail, resorting to current time!",
            exc_info=True,
        )
        return timezone.now()
    return parsedDatetime


def parseCorrespondentHeader(correspondentHeader: str) -> tuple[str, str]:
    name, address = parseaddr(correspondentHeader)
    if not address:
        logger.warning(
            "No mailaddress in header %s! Falling back to full header.",
            correspondentHeader,
        )
        return name, correspondentHeader
    try:
        email_validator.validate_email(address, check_deliverability=False)
    except email_validator.EmailNotValidError:
        logger.warning(
            "Invalid mailadress in %s! Falling back to full header.",
            correspondentHeader,
        )
        return name, correspondentHeader
    return name, address


def parseMailboxName(mailboxBytes: bytes) -> str:
    """Parses the mailbox name as received by the `fetchMailboxes` method in :mod:`core.utils.fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.
        The result must not be changed afterwards, otherwise opening the mailbox via this name is not possible!
    Args:
        mailboxBytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The serverside name of the mailbox
    """
    return imap_tools.imap_utf7.utf7_decode(mailboxBytes)
