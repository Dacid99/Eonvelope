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

"""Module with the :class:`EmailArchiverDaemon` class."""

from __future__ import annotations

import logging
import logging.handlers
import threading
import time
from typing import TYPE_CHECKING, override


if TYPE_CHECKING:
    from .models.Daemon import Daemon


class EmailArchiverDaemon(threading.Thread):
    """Daemon for continuous fetching and saving of mails to database."""

    def __init__(self, daemon: Daemon):
        """Constructor, sets up the daemon with the specification in `daemon`.

        Args:
            daemon: The data of the daemon.
        """
        self._daemon: Daemon = daemon
        super().__init__(daemon=True, name=str(self))

        self._stopEvent: threading.Event = threading.Event()

        self._setupLogger()

    @override
    def __str__(self) -> str:
        """Returns a string representation of the daemon instance.

        Returns:
            A string specifying the uuid and classname of this instance.
        """
        return f"{self.__class__.__name__} {self._daemon}"

    def _setupLogger(self) -> None:
        """Sets up the logger for the daemon with an additional filehandler for its own logfile."""
        self.logger = logging.getLogger(str(self))
        fileHandler = logging.handlers.RotatingFileHandler(
            filename=self._daemon.log_filepath,
            backupCount=self._daemon.log_backup_count,
            maxBytes=self._daemon.logfile_size,
        )
        self.logger.addHandler(fileHandler)

    @override
    def start(self) -> None:
        """Starts this daemon instance if it is inactive."""
        try:
            super().start()
        except RuntimeError:
            self.logger.debug(
                "Attempt to start this active daemon recorded.", stack_info=True
            )
            return

        self.logger.info("-----------------\nDaemon started\n-----------------")
        self._daemon.is_running = True
        self._daemon.save(update_fields=["is_running"])

    def stop(self) -> None:
        """Stops this daemon instance if it is active. The thread finishes by itself later."""

        if self._stopEvent.is_set():
            self.logger.debug(
                "Attempt to stop this inactive daemon recorded.", stack_info=True
            )
            return

        self._stopEvent.set()
        self.logger.info("-----------------\nDaemon stopped\n-----------------")
        self._daemon.is_running = False
        self._daemon.save(update_fields=["is_running"])

    def update(self) -> None:
        """Refreshes configuration from database."""
        self._daemon.refresh_from_db()
        self.logger.debug("Daemon updated.")

    @override
    def run(self) -> None:
        """The looping task execute on the daemon thread.

        If crashed tries to restart after time set in :attr:`_daemon.restart_time`
        and sets health flag of daemon to `False`.
        """
        try:
            while not self._stopEvent.is_set():
                self.cycle()
                time.sleep(self._daemon.cycle_interval)
            self.logger.info("%s finished successfully", self._daemon)
        except Exception:
            self.logger.exception(
                "%s crashed! Attempting to restart ...",
                str(self._daemon),
            )
            time.sleep(self._daemon.restart_time)
            self._daemon.is_healthy = False
            self._daemon.save(update_fields=["is_healthy"])
            self.run()

    def cycle(self) -> None:
        """The routine of this daemon.

        Fetches and saves mails. Logs the execution time.
        A successul run sets the daemon to healthy.

        Raises:
            Exception: Any exception thrown during execution of the routine.
        """
        self.logger.debug("---------------------------------------\nNew cycle")

        startTime = time.time()
        self._daemon.mailbox.fetch(self._daemon.fetching_criterion)
        endtime = time.time()

        self._daemon.is_healthy = True
        self._daemon.save(update_fields=["is_healthy"])

        self.logger.debug(
            "Cycle complete after %s seconds\n-------------------------------------------",
            endtime - startTime,
        )
