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
from .fileManagment import writeImages, writeAttachments, writeMessageToEML
import logging
from .mailParsing import parseMail
from .mailRendering import prerender
from .emailDBFeeding import insertEMail, insertMailbox
import datetime

from . import constants


def _getFilter(flag):
    if flag == constants.MailFetchingCriteria.DAILY:
        return "SINCE {date}".format(date=datetime.date.today().strftime("%d-%b-%Y"))
    else: 
        return flag



def testAccount(account):
    logger = logging.getLogger(__name__)

    logger.info(f"Testing {str(account)} ...")
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

    logger.info(f"Tested {str(account)} as {result}")
    return result



def scanMailboxes(mailAccount):
    logger = logging.Logger(__name__)

    logger.info(f"Searching mailboxes in {mailAccount}...")

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

    logger.info("Successfully searched mailboxes")
    return mailboxes

    

def fetchMails(mailbox, mailAccount, criterion):
    logger = logging.getLogger(__name__)

    logger.info(f"Fetching emails with criterion {criterion} from mailbox {mailbox} in account {mailAccount}...")
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

    logger.info("Successfully fetched emails")


    logger.info("Parsing emails from data and saving to db ...")
    status = True
    for mailData in mailDataList:
        try: 
            parsedMail = parseMail(mailData)

            if constants.ParsingConfiguration.THROW_OUT_SPAM and parsedMail[constants.ParsedMailKeys.Header.X_SPAM_FLAG]:
                logger.debug("Not saving email, it is flagged as spam.")
                continue

            if mailbox.save_toEML:
                writeMessageToEML(parsedMail)
                prerender(parsedMail)
            else:
                logger.debug(f"Not saving to eml for mailbox {mailbox.name}")


            if mailbox.save_attachments:
                writeAttachments(parsedMail)
            else:
                logger.debug(f"Not saving attachments for mailbox {mailbox.name}")
                
            
            if mailbox.save_images:
                writeImages(parsedMail)
            else:
                logger.debug(f"Not saving images for mailbox {mailbox.name}")

            insertEMail(parsedMail, mailAccount)
        
        except Exception as e:
            status = False
            logger.error(f"Error parsing and saving email with subject {parsedMail[constants.ParsedMailKeys.Header.SUBJECT]} from {parsedMail[constants.ParsedMailKeys.Header.DATE]}!", exc_info=True)
            continue

    if status:
        logger.info("Successfully parsed emails from data and saved to db.")
    else:
        logger.info("Parsed emails from data and saved to db with an error.")
        