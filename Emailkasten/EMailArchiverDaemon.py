# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import threading
import time

from rest_framework.response import Response

from . import constants
from .mailProcessing import fetchMails
from .Models.DaemonModel import DaemonModel
from .Models.AccountModel import AccountModel
from .Models.MailboxModel import MailboxModel


class EMailArchiverDaemon:
    """Daemon for continuous fetching and saving of mails to database.

    Attributes:
        logger (:class:`logging.Logger`): Logger for this instance with a filehandler for the daemons own logfile.
        thread (:class:`threading.Thread`): The thread that the daemon runs on.
        isRunning (bool): Whether this daemon instance is active.
        daemon (:class:`Emailkasten.Models.DaemonModel`): The database model of this daemon.
        mailbox (:class:`Emailkasten.Models.MailboxModel`): The database model of the mailbox this instance fetches from.
        account (:class:`Emailkasten.Models.AccountModel`): The database model of the account this instance fetches from.
    """

    runningDaemons: dict = {}
    """A static dictionary of all active daemon instances with their database IDs as keys."""


    @staticmethod
    def testDaemon(daemonModel: DaemonModel) -> Response:
        """Static method to test data for a daemon.

        Args:
            daemonModel: The data for the daemon to be tested.

        Returns:
            A response detailing what has happened.
        """
        try:
            newDaemon = EMailArchiverDaemon(daemonModel)
            newDaemon.cycle()
            return Response({
                'status': 'Daemon testrun was successful.',
                'account': daemonModel.mailbox.account.mail_address,
                'mailbox': daemonModel.mailbox.name, 'info': "Success"
                })
        except Exception as error:
            return Response({
                'status': 'Daemon testrun failed!',
                'account': daemonModel.mailbox.account.mail_address,
                'mailbox': daemonModel.mailbox.name,
                'info': str(error)
                })


    @staticmethod
    def startDaemon(daemonModel: DaemonModel) -> Response:
        """Static method to create, start and add a new daemon to :attr:`runningDaemons`.
        If it is already in the dict does nothing.

        Args:
            daemonModel: The data for the daemon.

        Returns:
            A response detailing what has been done.
        """
        if daemonModel.id not in EMailArchiverDaemon.runningDaemons:
            try:
                newDaemon = EMailArchiverDaemon(daemonModel)
                newDaemon.start()
                EMailArchiverDaemon.runningDaemons[daemonModel.id] = newDaemon
                daemonModel.is_running = True
                daemonModel.save()
                return Response({
                    'status': 'Daemon started',
                    'account': daemonModel.mailbox.account.mail_address,
                    'mailbox': daemonModel.mailbox.name
                    })
            except Exception:
                return Response({
                    'status': 'Daemon failed to start!',
                    'account': daemonModel.mailbox.account.mail_address,
                    'mailbox': daemonModel.mailbox.name
                    })
        else:
            return Response({
                'status':
                'Daemon already running',
                'account': daemonModel.mailbox.account.mail_address,
                'mailbox': daemonModel.mailbox.name
                })


    @staticmethod
    def stopDaemon(daemonModel: DaemonModel) -> Response:
        """Static method to stop and remove a daemon from :attr:`runningDaemons`.
        If it is not in the dict does nothing.

        Args:
            daemonModel: The data of the daemon.

        Returns:
            A response detailing what has been done.
        """
        if daemonModel.id in EMailArchiverDaemon.runningDaemons:
            oldDaemon = EMailArchiverDaemon.runningDaemons.pop( daemonModel.id )
            oldDaemon.stop()
            daemonModel.is_running = False
            daemonModel.save()
            return Response({
                'status': 'Daemon stopped',
                'account': daemonModel.mailbox.account.mail_address,
                'mailbox': daemonModel.mailbox.name
                })
        else:
            return Response({
                'status': 'Daemon not running',
                'account': daemonModel.mailbox.account.mail_address,
                'mailbox': daemonModel.mailbox.name
                })


    def __init__(self, daemon: DaemonModel) -> None:
        """Constructor, sets up the daemon with the specification in `daemon`.

        Args:
            daemon: The data of the daemon.
        """
        self.daemon: DaemonModel = daemon
        self.mailbox: MailboxModel = daemon.mailbox
        self.account: AccountModel = daemon.mailbox.account

        self.thread: threading.Thread|None = None
        self.isRunning: bool = False

        self.setupLogger()


    def setupLogger(self) -> None:
        """Sets up the logger for the daemon with an additional filehandler for its own logfile."""
        self.logger = logging.getLogger(__name__ + f".daemon_{self.daemon.id}")
        fileHandler = logging.FileHandler(self.daemon.log_filepath)
        self.logger.addHandler(fileHandler)


    def start(self) -> None:
        """Starts this daemon instance if it is not active.
        Creates and starts a new thread performing :func:`run`.
        """
        if not self.isRunning:
            self.logger.info("Starting %s ...", str(self.daemon))
            self.isRunning = True
            self.thread = threading.Thread(target = self.run)
            self.thread.start()
            self.logger.info("Successfully started daemon.")
        else:
            self.logger.info("EMailArchiverDaemon is already running.")


    def stop(self) -> None:
        """Stops this daemon instance if it is active.
        The thread finishes by itself later.
        """
        if self.isRunning:
            self.logger.info("Stopping %s ...", str(self.daemon))
            self.isRunning = False
        else:
            self.logger.info("EMailArchiverDaemon is not running.")


    def run(self) -> None:
        """The looping task execute on :attr:`thread`.
        Attempts to restart if crashed after time set in :attr:`constants.EMailArchiverDaemonConfiguration.RESTART_TIME`.
        """
        try:
            while self.isRunning:
                self.cycle()
                time.sleep(self.daemon.cycle_interval)
            self.logger.info("%s finished successfully", str(self.daemon))
        except Exception:
            self.logger.error("%s crashed! Attempting to restart ...", str(self.daemon), exc_info=True)
            time.sleep(constants.EMailArchiverDaemonConfiguration.RESTART_TIME)
            self.run()


    def cycle(self) -> None:
        """The routine of this daemon.
        Fetches and saves mails using :func:`Emailkasten.mailProcessing.fetchMails`. Logs the execution time.

        Raises:
            Exception: The exception thrown during execution of the routine.
        """
        self.logger.debug("---------------------------------------\nNew cycle")

        startTime = time.time()
        try:
            fetchMails(self.mailbox, self.account, self.mailbox.fetching_criterion)
            endtime = time.time()

        except Exception:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

        self.logger.debug("Cycle complete after %s seconds\n-------------------------------------------", endtime - startTime)
