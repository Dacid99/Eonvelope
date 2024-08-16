from .Fetchers.IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .Fetchers.IMAPFetcher import IMAPFetcher
from .Fetchers.POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .Fetchers.POP3Fetcher import POP3Fetcher
from .Fetchers.ExchangeFetcher import ExchangeFetcher
from .FileManager import FileManager
from .LoggerFactory import LoggerFactory
import datetime

class MailProcessor:
    UNSEEN = "UNSEEN"
    ALL = "ALL"
    RECENT = "RECENT"
    SINCE = "SINCE"
    NEW = "NEW"
    DAILY = "DAILY"

    @staticmethod
    def getFilter(flag):
        if flag == MailProcessor.DAILY:
            return "SINCE {date}".format(date=datetime.date.today().strftime("%d-%b-%Y"))
        else: 
            return flag


    @staticmethod
    def scanMailboxes(mailAccount):
        logger = LoggerFactory.getChildLogger(MailProcessor.__name__)

        logger.debug(f"Searching mailboxes in {mailAccount}...")

        if mailAccount.protocol == IMAPFetcher.PROTOCOL:
            with IMAPFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                mailboxes = imapMail.fetchMailboxes()

        elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            with IMAP_SSL_Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                mailboxes = imapMail.fetchMailboxes()

        elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
            mailboxes = ['INBOX']

        elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
            mailboxes = ['INBOX']

        elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
            with ExchangeFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as exchangeMail:

                mailboxes = exchangeMail.fetchMailboxes()

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            mailboxes = []

        logger.debug("Successfully searched mailboxes")

        return mailboxes

        
    @staticmethod
    def fetch(mailbox, mailAccount, criterion):
        logger = LoggerFactory.getChildLogger(MailProcessor.__name__)

        logger.debug(f"Fetching emails with criterion {criterion} from mailbox {mailbox} in account {mailAccount}...")
        if mailAccount.protocol == IMAPFetcher.PROTOCOL:
            with IMAPFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=MailProcessor.getFilter(criterion))

        elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            with IMAP_SSL_Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                mailDataList = imapMail.fetchBySearch(mailbox=mailbox.name, searchCriterion=MailProcessor.getFilter(criterion))

        elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
            with POP3Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as popMail:

                mailDataList = popMail.fetchAll()

        elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
            with POP3_SSL_Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as popMail:

                mailDataList = popMail.fetchAll()

        elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
            with ExchangeFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as exchangeMail:

                mailDataList = exchangeMail.fetchBySearch()

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            return

        logger.debug("Successfully fetched emails")


        logger.debug("Parsing emaildata ...")
        parsedMailsList = []
        for mailData in mailDataList:
            parsedMail = MailParser.parse(mail)
            parsedMailsList.append(parsedMail)
        logger.debug("Successfully parsed emaildata")


        if mailbox.save_toEML:
            logger.debug("Saving mails to eml files ...")
            for parsedMail in parsedMailsList:
                FileManager.writeMessageToEML(parsedMail)
            logger.debug("Successfully saved mails to eml files")
        else:
            logger.debug(f"Not saving to eml for mailbox {mailbox.name}")


        if mailbox.save_attachments:
            logger.debug("Saving attachments ...")
            for parsedMail in parsedMailsList:
                FileManager.writeAttachments(parsedMail)
            logger.debug("Successfully saved attachments")
        else:
            logger.debug(f"Not saving attachments for mailbox {mailbox.name}")

        logger.debug("Writing emails to database ...")
        for parsedMail in parsedMailsList:
            EMailDBFeeder.insertEMail(parsedMail, mailAccount)
        logger.debug("Successfully wrote emails to database")
