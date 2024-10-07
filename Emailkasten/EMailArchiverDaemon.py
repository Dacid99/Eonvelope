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

import time
import threading
from rest_framework.response import Response
from . import constants
import logging
from .MailProcessor import MailProcessor


class EMailArchiverDaemon:
    runningDaemons = {}
    
    @staticmethod
    def startDaemon(daemonModel):
        if not daemonModel.id in EMailArchiverDaemon.runningDaemons:
            try:
                newDaemon = EMailArchiverDaemon(daemonModel)
                newDaemon.start()
                EMailArchiverDaemon.runningDaemons[daemonModel.id] = newDaemon
                daemonModel.is_running = True
                daemonModel.save() 
                return Response({'status': 'Daemon started', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
            except Exception as e:
                return Response({'status': 'Daemon failed to start!', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        else:
            return Response({'status': 'Daemon already running', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        
    @staticmethod
    def stopDaemon(daemonModel):
        if daemonModel.id in EMailArchiverDaemon.runningDaemons:
            oldDaemon = EMailArchiverDaemon.runningDaemons.pop(daemonModel.id)
            oldDaemon.stop()
            daemonModel.is_running = False
            daemonModel.save()
            return Response({'status': 'Daemon stopped', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        else:
            return Response({'status': 'Daemon not running', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        

    def __init__(self, daemon):
        self.logger = logging.getLogger(__name__)
        self.thread = None
        self.isRunning = False
        
        self.daemon = daemon
        self.mailbox = daemon.mailbox
        self.account = daemon.mailbox.account


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
                time.sleep(self.daemon.cycle_interval)
            self.logger.info("EMailArchiverDaemon finished")
        except Exception as e:
            self.logger.critical("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(constants.EMailArchiverDaemonConfiguration.RESTART_TIME)
            self.run()

    def cycle(self):
        self.logger.debug("---------------------------------------\nNew cycle")
        startTime = time.time()
        try:
            MailProcessor.fetch(self.mailbox, self.account, self.mailbox.fetching_criterion)

            endtime = time.time()
            self.logger.debug(f"Cycle complete after {endtime - startTime} seconds\n-------------------------------------------")
                            
        except Exception as e:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

