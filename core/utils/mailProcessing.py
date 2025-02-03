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

"""Provides functions for processing the mails by fetching and storing them.
Combines functions from
:mod:`core.utils.emailDBFeeding`,
:mod:`core.utils.mailParsing` and
:mod:`core.utils.fetchers`.
Functions starting with _ are helpers and are used only within the scope of this module.

Functions:
    :func:`parseAndStoreMails`: Parses and stores maildata in the database.
    :func:`fetchAndProcessMails`: Fetches, parses and stores mails in the database.
    :func:`_isSpam`: Checks the spam headers of the parsed mail to decide whether the mail is spam.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from Emailkasten.utils import get_config

from ..constants import ParsedMailKeys
from ..models.EMailModel import EMailModel
from .emailDBFeeding import insertEMail
from .fileManagment import storeAttachments, storeImages, storeMessageAsEML
from .mailParsing import parseMail
from .mailRendering import prerender

if TYPE_CHECKING:
    from typing import Any

    from ..models.AccountModel import AccountModel
    from ..models.MailboxModel import MailboxModel


logger = logging.getLogger(__name__)


def _saveToEML(parsedMail: dict) -> None:
    """Save the parsed mail to eml file. Checks the database first.

    Note:
        Uses :func:`core.utils.fileManagment.storeMessageAsEML`
        and :func:`core.utils.mailRendering.prerender`.

    Args:
        parsedMail: The parsed mail to save as .eml.
    """
    try:
        email = EMailModel.objects.get(
            message_id=parsedMail[ParsedMailKeys.Header.MESSAGE_ID]
        )
        if not email.eml_filepath:
            storeMessageAsEML(parsedMail)
        if not email.prerender_filepath:
            prerender(parsedMail)
    except EMailModel.DoesNotExist:
        storeMessageAsEML(parsedMail)
        prerender(parsedMail)


def _saveAttachments(parsedMail: dict) -> None:
    """Save the parsed mail to eml file. Checks the database first.

    Todo:
        Should also check the db first.

    Note:
        Relies on :func:`core.utils.fileManagment.storeAttachments`.

    Args:
        parsedMail: The parsed mail to save attachments.
    """
    storeAttachments(parsedMail)


def _saveImages(parsedMail: dict) -> None:
    """Save the parsed mail to eml file. Checks the database first.

    Todo:
        Should also check the db first.

    Note:
        Relies on :func:`core.utils.fileManagment.storeImages`.

    Args:
        parsedMail: The parsed mail to save images.
    """
    storeImages(parsedMail)


def _parseAndStoreMails(mailDataList: list, mailbox: MailboxModel) -> None:
    """Parses and stores raw maildata in the database and storage.

    Note:
        Relies on the methods from :mod:`core.utils.mailParsing`
        and :mod:`core.utils.emailDBFeeding`.

    Args:
        mailDataList: The maildata to parse and store.
        mailbox: The data of the mailbox the data was fetched from.
    """

    logger.info("Parsing emails from data and saving to db ...")
    status = True
    for mailData in mailDataList:
        try:
            parsedMail = parseMail(mailData)

            if get_config("THROW_OUT_SPAM"):
                if _isSpam(parsedMail):
                    logger.debug("Not saving email, it is flagged as spam.")
                    continue

            if mailbox.save_toEML:
                _saveToEML(parsedMail)
            else:
                logger.debug("Not saving to eml for mailbox %s", mailbox.name)

            if mailbox.save_attachments:
                _saveAttachments(parsedMail)
            else:
                logger.debug("Not saving attachments for mailbox %s", mailbox.name)

            if mailbox.save_images:
                _saveImages(parsedMail)
            else:
                logger.debug("Not saving images for mailbox %s", mailbox.name)

            insertEMail(parsedMail, mailbox.account)

        except Exception:
            status = False
            logger.error(
                "Error parsing and saving email with subject %s from %s!",
                parsedMail[ParsedMailKeys.Header.SUBJECT],
                parsedMail[ParsedMailKeys.Header.DATE],
                exc_info=True,
            )
            continue

    if status:
        logger.info("Successfully parsed emails from data and saved to db.")
    else:
        logger.info("Parsed emails from data and saved to db with error.")


def fetchAndProcessMails(mailbox: MailboxModel, criterion: str) -> None:
    """Parses and stores raw maildata in the database and storage.

    Args:
        mailbox: The data of the mailbox to fetch from.
        criterion: A formatted criterion for message filtering
            as returned by :func:`core.utils.fetchers.IMAPFetcher.makeFetchingCriterion`.
    """

    mailDataList = mailbox.fetch(criterion)
    _parseAndStoreMails(mailDataList, mailbox)


def _isSpam(parsedMail: dict[str, Any]) -> bool:
    """Checks the spam headers of the parsed mail to decide whether the mail is spam.

    Args:
        parsedMail: The mail to be checked for spam.

    Returns:
        Whether the mail is considered spam.
    """
    return (
        parsedMail[ParsedMailKeys.Header.X_SPAM_FLAG] is not None
        and parsedMail[ParsedMailKeys.Header.X_SPAM_FLAG] != "NO"
    )
