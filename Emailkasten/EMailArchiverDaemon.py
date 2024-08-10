import time
import signal
import threading

from LoggerFactory import LoggerFactory
from DBManager import DBManager
from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from IMAPFetcher import IMAPFetcher
from POP3Fetcher import POP3Fetcher
from POP3_SSL_Fetcher import POP3_SSL_Fetcher
from ExchangeFetcher import ExchangeFetcher


class EMailArchiverDaemon:
    cyclePeriod = 60  #seconds
    __restartTime = 10
    dbHost = "192.168.178.109"
    dbUser = "root"
    dbPassword = "example"
    PROTOCOL = "IMAP_SSL"
    saveAttachments = True
    saveToEML= True

    def __init__(self):
        self.logger = LoggerFactory.getMainLogger()
        self.thread = None
        self.isRunning = False

    def start(self):
        self.isRunning = True
        self.logger.info("Starting EMailArchiverDaemon")
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping EMailArchiverDaemon")
        self.isRunning = False
        if self.thread:
            self.thread.join()
        self.logger.info("Gracefully stopped EMailArchiverDaemon")

    def run(self):
        try:
            while self.isRunning:
                self.cycle()
                time.sleep(EMailArchiverDaemon.cyclePeriod)
        except Exception as e:
            self.logger.critical("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(EMailArchiverDaemon.__restartTime)
            self.run()

    def cycle(self):
        self.logger.debug("---------------------------------------\nNew cycle")
        startTime = time.time()
        try:
            with DBManager(EMailArchiverDaemon.dbHost, EMailArchiverDaemon.dbUser, EMailArchiverDaemon.dbPassword, "email_archive", "utf8mb4", "utf8mb4_bin") as db:
                
                dbfeeder = EMailDBFeeder(db)

                if EMailArchiverDaemon.PROTOCOL == IMAPFetcher.PROTOCOL:
                    with IMAPFetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de") as imapMail:

                        parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                elif EMailArchiverDaemon.PROTOCOL == IMAP_SSL_Fetcher.PROTOCOL:
                    with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de") as imapMail:

                        parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                elif EMailArchiverDaemon.PROTOCOL == POP3Fetcher.PROTOCOL:
                    with POP3Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as imapMail:

                        parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                elif EMailArchiverDaemon.PROTOCOL == POP3_SSL_Fetcher.PROTOCOL:
                    with POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as imapMail:

                        parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                elif EMailArchiverDaemon.PROTOCOL == ExchangeFetcher.PROTOCOL:
                    with ExchangeFetcher() as exchangeMail:

                        parsedNewMails = exchangeMail.fetchBySearch()

                else:
                    self.logger.error("Can not fetch mails, protocol is not or incorrectly specified!")
                    parsedNewMails = []

                if EMailArchiverDaemon.saveToEML:
                    for mail in parsedNewMails:
                        mail.saveToEML()

                if EMailArchiverDaemon.saveAttachments:
                    for mail in parsedNewMails:
                        mail.saveAttachments()

                for mail in parsedNewMails:
                    dbfeeder.insert(mail)


            endtime = time.time()
            self.logger.debug(f"Cycle complete after {endtime - startTime} seconds\n-------------------------------------------")
                        
        except Exception as e:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

