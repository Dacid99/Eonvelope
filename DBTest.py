from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from POP3_SSL_Fetcher import POP3_SSL_Fetcher
from MailParser import MailParser
from DBManager import DBManager
import logging

logging.basicConfig(level=logging.DEBUG)

with DBManager("192.168.178.109", "root", "example", "email_archive", "utf8mb4", "utf8mb4_bin") as db:

    with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de", port=993) as imapMail:
    #with POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as popMail:

        parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")
        #parsedNewMails = popMail.fetchAll("")

        dbfeeder = EMailDBFeeder(db)
      
        for mail in parsedNewMails:
            print(mail)
            dbfeeder.insert(mail)