from .IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .IMAPFetcher import IMAPFetcher
from .POP3_SSL_Fetcher import POP3_SSL_Fetcher
from .POP3Fetcher import POP3Fetcher
from .ExchangeFetcher import ExchangeFetcher
from .FileManager import FileManager

class MailProcessor:
    UNSEEN = "UNSEEN"
    ALL = "ALL"
    RECENT = "RECENT"

    @staticmethod
    def fetch(mailAccount, criterion):
        if mailAccount.protocol == IMAPFetcher.PROTOCOL:
            with IMAPFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                parsedMails = imapMail.fetchBySearch(searchCriterion=criterion)

        elif mailAccount.protocol == IMAP_SSL_Fetcher.PROTOCOL:
            with IMAP_SSL_Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                parsedMails = imapMail.fetchBySearch(searchCriterion=criterion)

        elif mailAccount.protocol == POP3Fetcher.PROTOCOL:
            with POP3Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                parsedMails = imapMail.fetchBySearch(searchCriterion=criterion)

        elif mailAccount.protocol == POP3_SSL_Fetcher.PROTOCOL:
            with POP3_SSL_Fetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as imapMail:

                parsedMails = imapMail.fetchBySearch(searchCriterion=criterion)

        elif mailAccount.protocol == ExchangeFetcher.PROTOCOL:
            with ExchangeFetcher(username=mailAccount.mail_address, password=mailAccount.password, host=mailAccount.mail_host, port=mailAccount.mail_host_port) as exchangeMail:

                parsedMails = exchangeMail.fetchBySearch()

        else:
            logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
            parsedMails = []

        if mailAccount.save_toEML:
            logger.debug("Saving mail to eml file ...")
            for mail in parsedMails:
                FileManager.writeMessageToEML(mail)
            logger.debug("Success")
        else:
            logger.debug("Not saving to eml, it is toggled off")


        if mailAccount.save_attachments:
            logger.debug("Saving attachments ...")
            for mail in parsedMails:
                FileManager.writeAttachments(mail)
            logger.debug("Success")
        else:
            logger.debug("Not saving attachments, it is toggled off")


        return parsedMails
