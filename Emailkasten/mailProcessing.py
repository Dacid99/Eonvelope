'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from .Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .Fetchers.IMAPFetcher import IMAPFetcher
from .Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .Fetchers.POP3Fetcher import POP3Fetcher
from .Fetchers.ExchangeFetcher import ExchangeFetcher
from .FileManagment import writeImages, writeAttachments, writeMessageToEML
import logging
from .MailParsing import parseMail
from .MailRendering import prerender
from .EMailDBFeeding import insertEMail, insertMailbox
import datetime

from . import constants


def _getFilter(flag):
    if flag == constants.MailFetchingCriteria.DAILY:
        return "SINCE {date}".format(date=datetime.date.today().strftime("%d-%b-%Y"))
    else: 
        return flag



def testAccount(account):
    logger = logging.getLogger(__name__)

    logger.debug(f"Testing {str(account)} ...")
    if account.protocol == IMAPFetcher.PROTOCOL:
            result = IMAPFetcher.test(account)

    elif account.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            result = IMAP_SSL_Fetcher.test(account)

    elif account.protocol == POP3Fetcher.PROTOCOL:
            result = POP3Fetcher.test(account)

    elif account.protocol == POP3_SSL_Fetcher.PROTOCOL:
            result = POP3_SSL_Fetcher.test(account)

    elif account.protocol == ExchangeFetcher.PROTOCOL:
            result = ExchangeFetcher.test(account)

    else:
        logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
        result = False

    logger.debug(f"Tested {str(account)} as {result}")
    return result



def scanMailboxes(mailAccount):
    logger = logging.Logger(__name__)

    logger.debug(f"Searching mailboxes in {mailAccount}...")

    if mailAccount.protocol == IMAPFetcher.PROTOCOL:
        with IMAPFetcher(mailAccount) as imapMail:

            mailboxes = imapMail.fetchMailboxes()

    elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        with IMAP_SSL_Fetcher(mailAccount) as imapMail:

            mailboxes = imapMail.fetchMailboxes()

    elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
        mailboxes = ['INBOX']

    elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
        mailboxes = ['INBOX']

    elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
        with ExchangeFetcher(mailAccount) as exchangeMail:

            mailboxes = exchangeMail.fetchMailboxes()

    else:
        logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
        mailboxes = []
        
    for mailbox in mailboxes:
        insertMailbox(mailbox, mailAccount)

    logger.debug("Successfully searched mailboxes")
    return mailboxes

    

def fetchMails(mailbox, mailAccount, criterion):
    logger = logging.getLogger(__name__)

    logger.debug(f"Fetching emails with criterion {criterion} from mailbox {mailbox} in account {mailAccount}...")
    if mailAccount.protocol == IMAPFetcher.PROTOCOL:
        with IMAPFetcher(mailAccount) as imapMail:

            mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=_getFilter(criterion))

    elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
        with IMAP_SSL_Fetcher(mailAccount) as imapMail:

            mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=_getFilter(criterion))

    elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
        with POP3Fetcher(mailAccount) as popMail:

            mailDataList = popMail.fetchAll()

    elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
        with POP3_SSL_Fetcher(mailAccount) as popMail:

            mailDataList = popMail.fetchAll()

    elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
        with ExchangeFetcher(mailAccount) as exchangeMail:

            mailDataList = exchangeMail.fetchBySearch() #incomplete

    else:
        logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
        return

    logger.debug("Successfully fetched emails")


    logger.debug("Parsing emaildata ...")
    parsedMailsList = []
    for mailData in mailDataList:
        parsedMail = parseMail(mailData)
        parsedMailsList.append(parsedMail)
    logger.debug("Successfully parsed emaildata")


    if mailbox.save_toEML:
        logger.debug("Saving mails to eml files ...")
        for parsedMail in parsedMailsList:
            writeMessageToEML(parsedMail)
            prerender(parsedMail)
        logger.debug("Successfully saved mails to eml files")
    else:
        logger.debug(f"Not saving to eml for mailbox {mailbox.name}")


    if mailbox.save_attachments:
        logger.debug("Saving attachments ...")
        for parsedMail in parsedMailsList:
            writeAttachments(parsedMail)
        logger.debug("Successfully saved attachments")
    else:
        logger.debug(f"Not saving attachments for mailbox {mailbox.name}")
        
    
    if mailbox.save_images:
        logger.debug("Saving images ...")
        for parsedMail in parsedMailsList:
            writeImages(parsedMail)
        logger.debug("Successfully saved images")
    else:
        logger.debug(f"Not saving images for mailbox {mailbox.name}")


    logger.debug("Writing emails to database ...")
    for parsedMail in parsedMailsList:
        insertEMail(parsedMail, mailAccount)
    logger.debug("Successfully wrote emails to database")



        