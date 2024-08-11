

class MailFetcher:
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

        if self.mailAccount.save_toEML:
            for mail in parsedMails:
                mail.saveToEML()

        if self.mailAccount.save_attachments:
            for mail in parsedMails:
                mail.saveAttachments()

        return parsedMails