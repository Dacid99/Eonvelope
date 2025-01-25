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

from .utils.mailProcessing import fetchAndProcessMails
from core.models.DaemonModel import DaemonModel


class EMailArchiverDaemon(threading.Thread):
    """Daemon for continuous fetching and saving of mails to database.

    Attributes:
        logger (:class:`logging.Logger`): Logger for this instance with a filehandler for the daemons own logfile.
        _stopEvent (:class:`threading.Event`): Event flag to control whether this daemon instance is running.
        _daemon (:class:`core.models.DaemonModel`): The database model of this daemon.
    """


    def __init__(self, daemonModel: DaemonModel) -> None:
        """Constructor, sets up the daemon with the specification in `daemon`.

        Args:
            daemonModel: The data of the daemon.
        """
        super().__init__(daemon=True, name=__name__ + f'_{daemonModel.uuid}')
        self._daemonModel: DaemonModel = daemonModel

        self._stopEvent: threading.Event = threading.Event()

        self._setupLogger()


    def _setupLogger(self) -> None:
        """Sets up the logger for the daemon with an additional filehandler for its own logfile."""
        self.logger = logging.getLogger(__name__ + f".daemon_{self._daemonModel.id}")
        fileHandler = logging.FileHandler(self._daemonModel.log_filepath)
        self.logger.addHandler(fileHandler)


    def start(self) -> None:
        """Starts this daemon instance if it is inactive."""
        try:
            super().start()
        except RuntimeError:
            self.logger.debug("Attempt to start this active daemon recorded.", stack_info=True)
            return

        self.logger.info("-----------------\nDaemon started\n-----------------")
        self._daemonModel.is_running = True
        self._daemonModel.save(update_fields = ['is_running'])


    def stop(self) -> None:
        """Stops this daemon instance if it is active.
        The thread finishes by itself later.
        """
        if self._stopEvent.is_set():
            self.logger.debug("Attempt to stop this inactive daemon recorded.", stack_info=True)
            return

        self._stopEvent.set()
        self.logger.info("-----------------\nDaemon stopped\n-----------------")
        self._daemonModel.is_running = False
        self._daemonModel.save(update_fields = ['is_running'])


    def update(self) -> None:
        """Refreshes configuration from database."""
        self._daemonModel.refresh_from_db()
        self.logger.debug('Daemon updated.')


    def run(self) -> None:
        """The looping task execute on the daemon thread.
        If crashed tries to restart after time set in :attr:`_daemonModel.restart_time`
        and sets health flag of daemon to `False`.
        """
        try:
            while not self._stopEvent.is_set():
                self.cycle()
                time.sleep(self._daemonModel.cycle_interval)
            self.logger.info("%s finished successfully", str(self._daemonModel))
        except Exception:
            self.logger.error("%s crashed! Attempting to restart ...", str(self._daemonModel), exc_info=True)
            time.sleep(self._daemonModel.restart_time)
            self._daemonModel.is_healthy = False
            self._daemonModel.save(update_fields=['is_healthy'])
            self.run()


    def cycle(self) -> None:
        """The routine of this daemon.
        Fetches and saves mails using :func:`core.utils.mailProcessing.fetchAndProcessMails`. Logs the execution time.
        A successul run sets the daemon to healthy.

        Raises:
            Exception: Any exception thrown during execution of the routine.
        """
        self.logger.debug("---------------------------------------\nNew cycle")

        startTime = time.time()
        fetchAndProcessMails(self._daemonModel.mailbox, self._daemonModel.fetching_criterion)
        endtime = time.time()

        self._daemonModel.is_healthy = True
        self._daemonModel.save(update_fields=['is_healthy'])

        self.logger.debug("Cycle complete after %s seconds\n-------------------------------------------",
                          endtime - startTime)
