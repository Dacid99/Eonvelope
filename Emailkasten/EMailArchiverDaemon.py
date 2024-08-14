import time
import threading

from .LoggerFactory import LoggerFactory
from .MailProcessor import MailProcessor
from .EMailDBFeeder import EMailDBFeeder


class EMailArchiverDaemon:
    restartTime = 10
    cyclePeriod = 60

    def __init__(self, mailbox):
        self.logger = LoggerFactory.getMainLogger()
        self.thread = None
        self.isRunning = False

        self.mailbox = mailbox
        self.account = mailbox.account


    def start(self):
        self.logger.info("Starting EMailArchiverDaemon")
        self.isRunning = True
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping EMailArchiverDaemon")
        self.isRunning = False

    def run(self):
        try:
            while self.isRunning:
                self.cycle()
                time.sleep(self.mailbox.cycle_interval)
            self.logger.info("EMailArchiverDaemon finished")
        except Exception as e:
            self.logger.critical("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(EMailArchiverDaemon.restartTime)
            self.run()

    def cycle(self):
        self.logger.debug("---------------------------------------\nNew cycle")
        startTime = time.time()
        try:
            parsedNewMails = MailProcessor.fetch(self.mailbox, self.account, self.mailbox.fetching_criterion)

            for mail in parsedNewMails:
                EMailDBFeeder.insertEMail(mail)

            endtime = time.time()
            self.logger.debug(f"Cycle complete after {endtime - startTime} seconds\n-------------------------------------------")
                            
        except Exception as e:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

