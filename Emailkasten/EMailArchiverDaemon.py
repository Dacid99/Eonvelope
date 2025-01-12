# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`EMailArchiverDaemon` class."""

import logging
import threading
import time

from rest_framework.response import Response

from .constants import EMailArchiverDaemonConfiguration
from .mailProcessing import fetchAndProcessMails
from .Models.DaemonModel import DaemonModel
from .Models.AccountModel import AccountModel
from .Models.MailboxModel import MailboxModel


class EMailArchiverDaemon(threading.Thread):
    """Daemon for continuous fetching and saving of mails to database.

    Attributes:
        logger (:class:`logging.Logger`): Logger for this instance with a filehandler for the daemons own logfile.
        _stopEvent (:class:`threading.Event`): Event flag to control whether this daemon instance is running.
        _daemon (:class:`Emailkasten.Models.DaemonModel`): The database model of this daemon.
    """

    runningDaemons: dict = {}
    """A static dictionary of all active daemon instances with their database IDs as keys."""


    @staticmethod
    def testDaemon(daemonModel: DaemonModel) -> bool:
        """Static method to test data for a daemon.

        Args:
            daemonModel: The data for the daemon to be tested.

        Returns:
            Whether the test was successful.
        """
        try:
            newDaemon = EMailArchiverDaemon(daemonModel)
            newDaemon.logger.debug("Testing daemon %s ...", str(daemonModel))
            newDaemon.cycle()
            newDaemon.logger.debug("Successfully tested daemon %s.", str(daemonModel))
            return daemonModel.is_healthy
        except Exception:
            newDaemon.logger.error("Error while testing daemon %s!", str(daemonModel), exc_info=True)
            return False


    @staticmethod
    def startDaemon(daemonModel: DaemonModel) -> bool:
        """Static method to create, start and add a new daemon to :attr:`runningDaemons`.
        If it is already in the dict does nothing.

        Args:
            daemonModel: The data for the daemon.

        Returns:
            `True` if the daemon was started, `False` if it was already running.
        """
        if daemonModel.id not in EMailArchiverDaemon.runningDaemons:
            newDaemon = EMailArchiverDaemon(daemonModel)
            newDaemon.start()
            EMailArchiverDaemon.runningDaemons[daemonModel.id] = newDaemon
            return True
        else:
            return False


    @staticmethod
    def stopDaemon(daemonModel: DaemonModel) -> bool:
        """Static method to stop and remove a daemon from :attr:`runningDaemons`.
        If it is not in the dict does nothing.

        Args:
            daemonModel: The data of the daemon.

        Returns:
            `True` if the daemon was stopped, `False` if it wasnt running.
        """
        if daemonModel.id in EMailArchiverDaemon.runningDaemons:
            oldDaemon = EMailArchiverDaemon.runningDaemons.pop(daemonModel.id)
            try:
                oldDaemon.stop()
            except RuntimeError:
                oldDaemon.logger.error("Daemon was already stopped!", exc_info=True)
            return True
        else:
            return False


    def __init__(self, daemon: DaemonModel) -> None:
        """Constructor, sets up the daemon with the specification in `daemon`.

        Args:
            daemon: The data of the daemon.
        """
        super().__init__(daemon=True, name=__name__ + f'_{daemon.uuid}')
        self._daemon: DaemonModel = daemon

        self._stopEvent: threading.Event = threading.Event()

        self._setupLogger()


    def _setupLogger(self) -> None:
        """Sets up the logger for the daemon with an additional filehandler for its own logfile."""
        self.logger = logging.getLogger(__name__ + f".daemon_{self._daemon.id}")
        fileHandler = logging.FileHandler(self._daemon.log_filepath)
        self.logger.addHandler(fileHandler)


    def start(self) -> None:
        """Starts this daemon instance.

        Raises:
            RuntimeError: If called on a running instance.
        """
        super().start()
        self.logger.info("EMailArchiverDaemon started.")
        self.daemon.is_running = True
        self.daemon.save(update_fields = ['is_running'])


    def stop(self) -> None:
        """Stops this daemon instance if it is active.
        The thread finishes by itself later.

        Raises:
            RuntimeError: If called on a stopped thread.
        """
        if self._stopEvent.is_set():
            raise RuntimeError("threads can only be stopped once")

        self._stopEvent.set()
        self.logger.info("EMailArchiverDaemon stopped.")
        self.daemon.is_running = False
        self.daemon.save(update_fields = ['is_running'])


    def reset(self) -> None:
        """Resets the daemon stop flag, refreshes configuration from database."""
        self.update()
        self._stopEvent.clear()


    def update(self) -> None:
        """Refreshes configuration from database."""
        self._daemon.refresh_from_db()


    def run(self) -> None:
        """The looping task execute on :attr:`thread`.
        If crashed tries to restart after time set in :attr:`constants.EMailArchiverDaemonConfiguration.RESTART_TIME`
        and sets health flag of daemon to `False`.
        """
        try:
            while not self._stopEvent.is_set():
                self.cycle()
                time.sleep(self._daemon.cycle_interval)
            self.logger.info("%s finished successfully", str(self._daemon))
        except Exception:
            self.logger.error("%s crashed! Attempting to restart ...", str(self._daemon), exc_info=True)
            self._daemon.is_healthy = False
            self._daemon.save(update_fields=['is_healthy'])
            time.sleep(EMailArchiverDaemonConfiguration.RESTART_TIME)
            self.run()


    def cycle(self) -> None:
        """The routine of this daemon.
        Fetches and saves mails using :func:`Emailkasten.mailProcessing.fetchAndProcessMails`. Logs the execution time.
        A successul run sets the daemon to healthy.

        Raises:
            Exception: The exception thrown during execution of the routine.
        """
        self.logger.debug("---------------------------------------\nNew cycle")

        startTime = time.time()
        fetchAndProcessMails(self.daemon.mailbox, self.daemon.account, self.daemon.fetching_criterion)
        endtime = time.time()

        self._daemon.is_healthy = True
        self._daemon.save(update_fields=['is_healthy'])

        self.logger.debug("Cycle complete after %s seconds\n-------------------------------------------",
                          endtime - startTime)
