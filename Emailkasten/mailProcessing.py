# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Provides functions for processing the mails by fetching and storing them.
Combines functions from :mod:`Emailkasten.emailDBFeeding`, :mod:`Emailkasten.mailParsing` and :mod:`Emailkasten.Fetchers`.
Functions starting with _ are helpers and are used only within the scope of this module.

Functions:
    :func:`testAccount`: Tests whether the data in an accountmodel is correct and allows connecting and logging in to the mailhost and account.
    :func:`scanMailboxes`: Scans the given mailaccount for mailboxes, inserts them into the database.
    :func:`fetchMails`: Fetches maildata from a given mailbox in a mailaccount based on a search criterion and stores them in the database.
    :func:`_isSpam`: Checks the spam headers of the parsed mail to decide whether the mail is spam.

Global variables:
    logger (:python::class:`logging.Logger`): The logger for this module.
"""

import logging

from . import constants
from .constants import TestStatusCodes
from .emailDBFeeding import insertEMail, insertMailbox
from .Fetchers.ExchangeFetcher import ExchangeFetcher
from .Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .Fetchers.IMAPFetcher import IMAPFetcher
from .Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .Fetchers.POP3Fetcher import POP3Fetcher
from .fileManagment import storeAttachments, storeImages, storeMessageAsEML
from .mailParsing import parseMail, parseMailbox
from .mailRendering import prerender

logger = logging.getLogger(__name__)


def testAccount(account):
    """Tests whether the data in an accountmodel is correct and allows connecting and logging in to the mailhost and account.
    The :attr:`Emailkasten.Models.AccountModel.is_healthy` flag is set according to the result by the Fetcher class, e.g. :class:`Emailkasten.Fetchers.IMAPFetcher`.
    Relies on the `test` static method of the :mod:`Emailkasten.Fetchers` classes.

    Args:
        account (:class:`Emailkasten.Models.AccountModel`): The account data to test.

    Returns:
        bool: The result of the test.
    """

    logger.info("Testing %s ...", str(account))
    if account.protocol == IMAPFetcher.PROTOCOL:
        result = IMAPFetcher.testAccount(account)

    elif account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        result = IMAP_SSL_Fetcher.testAccount(account)

    elif account.protocol == POP3Fetcher.PROTOCOL:
        result = POP3Fetcher.testAccount(account)

    elif account.protocol == POP3_SSL_Fetcher.PROTOCOL:
        result = POP3_SSL_Fetcher.testAccount(account)

    elif account.protocol == ExchangeFetcher.PROTOCOL:
        result = ExchangeFetcher.testAccount(account)

    else:
        logger.error("Account %s has unknown protocol!", str(account))
        account.is_healthy = False
        account.save()
        result = TestStatusCodes.ERROR

    logger.info("Successfully tested account to be %s.", result)

    return result


def testMailbox(mailbox):
    """Tests whether the data in a mailboxmodel is correct and allows connecting and opening the account and mailbox.
    The :attr:`Emailkasten.Models.MailboxModel.is_healthy` flag is set according to the result by the Fetcher class, e.g. :class:`Emailkasten.Fetchers.IMAPFetcher`.
    Relies on the `test` static method of the :mod:`Emailkasten.Fetchers` classes.

    Args:
        mailbox (:class:`Emailkasten.Models.MailboxModel`): The mailbox data to test.

    Returns:
        int: The result of the test.
    """

    logger.info("Testing %s ...", str(mailbox))
    if mailbox.account.protocol == IMAPFetcher.PROTOCOL:
        result = IMAPFetcher.testMailbox(mailbox)

    elif mailbox.account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        result = IMAP_SSL_Fetcher.testMailbox(mailbox)

    elif mailbox.account.protocol == POP3Fetcher.PROTOCOL:
        result = POP3Fetcher.testMailbox(mailbox)

    elif mailbox.account.protocol == POP3_SSL_Fetcher.PROTOCOL:
        result = POP3_SSL_Fetcher.testMailbox(mailbox)

    elif mailbox.account.protocol == ExchangeFetcher.PROTOCOL:
        result = ExchangeFetcher.testMailbox(mailbox)

    else:
        logger.error("Account %s has unknown protocol!", str(mailbox.account))
        mailbox.is_healthy = False
        mailbox.save()
        result = TestStatusCodes.ERROR

    logger.info("Successfully tested mailbox to be %s.", result)

    return result



def scanMailboxes(account):
    """Scans the given mailaccount for mailboxes, parses and inserts them into the database.
    For POP3 accounts, there is only one mailbox, it defaults to INBOX.
    Relies on the :func:`fetchMailboxes` method of the :mod:`Emailkasten.Fetchers` classes, :func:`parseMailbox` from :mod:`Emailkasten.mailParsing` and :func:`insertMailbox` from :mod:`Emailkasten.emailDBFeeding`.

    Args:
        account (:class:`Emailkasten.Models.AccountModel`): The data of the account to scan for mailboxes.

    Returns:
        None
    """

    logger.info("Searching mailboxes in %s...", account)

    if account.protocol == IMAPFetcher.PROTOCOL:
        with IMAPFetcher(account) as imapMail:

            mailboxes = imapMail.fetchMailboxes()

    elif account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        with IMAP_SSL_Fetcher(account) as imapMail:

            mailboxes = imapMail.fetchMailboxes()

    elif account.protocol == POP3Fetcher.PROTOCOL:
        mailboxes = ['INBOX']

    elif account.protocol == POP3_SSL_Fetcher.PROTOCOL:
        mailboxes = ['INBOX']

    elif account.protocol == ExchangeFetcher.PROTOCOL:
        with ExchangeFetcher(account) as exchangeMail:

            mailboxes = exchangeMail.fetchMailboxes()

    else:
        logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
        mailboxes = []

    for mailbox in mailboxes:
        parsedMailbox = parseMailbox(mailbox)
        insertMailbox(parsedMailbox, account)

    logger.info("Successfully searched mailboxes")




def fetchMails(mailbox, account, criterion):
    """Fetches maildata from a given mailbox in a mailaccount based on a search criterion and stores them in the database and storage.
    For POP3 accounts, there is only one mailbox and no options for specific queries, so all messages are fetched.
    Relies on the :func:`fetchBySearch` and :func:`fetchAll` methods of the :mod:`Emailkasten.Fetchers` classes, the methods from :mod:`Emailkasten.mailParsing` and :mod:`Emailkasten.emailDBFeeding`.

    Args:
        mailbox (:class:`Emailkasten.Models.MailboxModel`): The data of the mailbox to fetch from.
        account (:class:`Emailkasten.Models.AccountModel`): The data of the mailaccount to fetch from.
        criterion (str): A formatted criterion for message filtering as returned by :func:`Emailkasten.Fetchers.IMAPFetcher.makeFetchingCriterion`.
            If none is given, defaults to RECENT inside :func:`Emailkasten.Fetchers.IMAPFetcher.fetchBySearch`.

    Returns:
        None
    """

    logger.info("Fetching emails with criterion %s from mailbox %s in account %s...", criterion, mailbox, account)
    if account.protocol == IMAPFetcher.PROTOCOL:
        with IMAPFetcher(account) as imapMail:

            mailDataList = imapMail.fetchBySearch(mailbox=mailbox, criterion=criterion)

    elif account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        with IMAP_SSL_Fetcher(account) as imapMail:

            mailDataList = imapMail.fetchBySearch(mailbox=mailbox, criterion=criterion)

    elif account.protocol == POP3Fetcher.PROTOCOL:
        with POP3Fetcher(account) as popMail:

            mailDataList = popMail.fetchAll(mailbox)

    elif account.protocol == POP3_SSL_Fetcher.PROTOCOL:
        with POP3_SSL_Fetcher(account) as popMail:

            mailDataList = popMail.fetchAll(mailbox)

    elif account.protocol == ExchangeFetcher.PROTOCOL:
        with ExchangeFetcher(account) as exchangeMail:

            mailDataList = exchangeMail.fetchBySearch() #incomplete

    else:
        logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
        return

    logger.info("Successfully fetched emails")


    logger.info("Parsing emails from data and saving to db ...")
    status = True
    for mailData in mailDataList:
        try:
            parsedMail = parseMail(mailData)

            if constants.ParsingConfiguration.THROW_OUT_SPAM:
                if _isSpam(parsedMail):
                    logger.debug("Not saving email, it is flagged as spam.")
                    continue

            if mailbox.save_toEML:
                storeMessageAsEML(parsedMail)
                prerender(parsedMail)
            else:
                logger.debug("Not saving to eml for mailbox %s", mailbox.name)


            if mailbox.save_attachments:
                storeAttachments(parsedMail)
            else:
                logger.debug("Not saving attachments for mailbox %s", mailbox.name)


            if mailbox.save_images:
                storeImages(parsedMail)
            else:
                logger.debug("Not saving images for mailbox %s", mailbox.name)

            insertEMail(parsedMail, account)

        except Exception:
            status = False
            logger.error("Error parsing and saving email with subject %s from %s!", parsedMail[constants.ParsedMailKeys.Header.SUBJECT], parsedMail[constants.ParsedMailKeys.Header.DATE], exc_info=True)
            continue

    if status:
        logger.info("Successfully parsed emails from data and saved to db.")
    else:
        logger.info("Parsed emails from data and saved to db with an error.")


def _isSpam(parsedMail):
    """Checks the spam headers of the parsed mail to decide whether the mail is spam.

    Args:
        parsedMail (dict): The mail to be checked for spam.

    Returns:
        bool: Whether the mail is considered spam.
    """
    return parsedMail[constants.ParsedMailKeys.Header.X_SPAM_FLAG] and parsedMail[constants.ParsedMailKeys.Header.X_SPAM_FLAG] != 'NO'
