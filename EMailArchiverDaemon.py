import logging
import time

from DBManager import DBManager
from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher

class EMailArchiverDaemon:
    cyclePeriod = 60  #seconds
    __restartTime = 10
    dbHost = "192.168.178.109"
    dbUser = "root"
    dbPassword = "example"

    def start(self):
        try:
            while True:
                self.cycle()
                time.sleep(EMailArchiverDaemon.cyclePeriod)
        except Exception as e:
            logging.error("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(EMailArchiverDaemon.__restartTime)
            self.start()

    def cycle(self):
        try:
            with DBManager(EMailArchiverDaemon.dbHost, EMailArchiverDaemon.dbUser, EMailArchiverDaemon.dbPassword, "email_archive", "utf8mb4", "utf8mb4_bin") as db:
                
                dbfeeder = EMailDBFeeder(db)
                
                with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as imapMail:

                    parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                    for mail in parsedNewMails:
                        dbfeeder.insert(mail)
                        
        except Exception as e:
            logging.error("Error during daemon cycle execution!", exc_info=True)
            raise