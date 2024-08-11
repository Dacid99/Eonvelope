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
    restartTime = 10

    def __init__(self, account):
        self.logger = LoggerFactory.getMainLogger()
        self.thread = None
        self.isRunning = False

        self.mailAccount = account


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
                time.sleep(self.mailAccount.cycle_interval)
        except Exception as e:
            self.logger.critical("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(EMailArchiverDaemon.restartTime)
            self.run()

    def cycle(self):
        self.logger.debug("---------------------------------------\nNew cycle")
        startTime = time.time()
        try:
            with DBManager(EMailArchiverDaemon.dbHost, EMailArchiverDaemon.dbUser, EMailArchiverDaemon.dbPassword, "email_archive", "utf8mb4", "utf8mb4_bin") as db:
                
                dbfeeder = EMailDBFeeder(db)

                parsedNewMails = MailProcessor.fetch(self.account, MailFetcher.RECENT)

                for mail in parsedNewMails:
                    dbfeeder.insert(mail)

            endtime = time.time()
            self.logger.debug(f"Cycle complete after {endtime - startTime} seconds\n-------------------------------------------")
                        
        except Exception as e:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

