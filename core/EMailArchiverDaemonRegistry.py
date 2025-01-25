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

"""Module with the :class:`EMailArchiverDaemonRegistry class."""

import logging

from .EMailArchiverDaemon import EMailArchiverDaemon
from core.models.DaemonModel import DaemonModel


class EMailArchiverDaemonRegistry:
    """Daemon registry for managment of the running :class:`core.EMailArchiverDaemon.EMailArchiverDaemon` instances."""

    _runningDaemons: dict = {}
    """A static dictionary of all active daemon instances with their database IDs as keys."""

    logger: logging.Logger = logging.getLogger(__name__)
    """The logger instance for this singleton."""

    @classmethod
    def isRunning(cls, daemonModel: DaemonModel) -> bool:
        """Class method to check whether a daemon is active.

        Args:
            daemonModel: The data for the daemon to check.

        Returns:
            Whether the daemon is active.
        """
        return daemonModel.id in cls._runningDaemons

    @classmethod
    def updateDaemon(cls, daemonModel: DaemonModel):
        """Class method to update a daemon instance.

        Args:
            daemonModel: The data for the daemon to update.
        """
        if cls.isRunning(daemonModel):
            daemonInstance = cls._runningDaemons[daemonModel.id]
            daemonInstance.update()
            cls.logger.debug('Updated daemon %s', str(daemonModel))

    @classmethod
    def testDaemon(cls, daemonModel: DaemonModel) -> bool:
        """Class method to test data for a daemon.

        Args:
            daemonModel: The data for the daemon to be tested.

        Returns:
            Whether the test was successful.
        """
        try:
            newDaemon = EMailArchiverDaemon(daemonModel)
            cls.logger.debug("Testing daemon %s ...", str(daemonModel))
            newDaemon.cycle()
            cls.logger.debug("Successfully tested daemon %s.", str(daemonModel))
            daemonModel.refresh_from_db()
            return daemonModel.is_healthy
        except Exception:
            cls.logger.error("Failed to test daemon %s !", str(daemonModel), exc_info=True)
            return False


    @classmethod
    def startDaemon(cls, daemonModel: DaemonModel) -> bool:
        """Class method to create, start and add a new daemon to :attr:`_runningDaemons`.

        Args:
            daemonModel: The data for the daemon.

        Returns:
            `True` if the daemon was started, `False` if it was already running.
        """
        if not cls.isRunning(daemonModel):
            cls.logger.debug("Starting daemon %s ...", str(daemonModel))
            newDaemon = EMailArchiverDaemon(daemonModel)
            newDaemon.start()
            cls._runningDaemons[daemonModel.id] = newDaemon
            cls.logger.debug("Successfully started daemon %s .", str(daemonModel))
            return True
        else:
            cls.logger.debug("Did not start daemon %s, it was already running.", str(daemonModel))
            return False


    @classmethod
    def stopDaemon(cls, daemonModel: DaemonModel) -> bool:
        """Class method to stop and remove a daemon from :attr:`_runningDaemons`.

        Args:
            daemonModel: The data of the daemon.

        Returns:
            `True` if the daemon was stopped, `False` if it wasnt running.
        """
        if cls.isRunning(daemonModel):
            cls.logger.debug("Stopping daemon %s ...", str(daemonModel))
            daemon = cls._runningDaemons.pop(daemonModel.id)
            daemon.stop()
            cls.logger.debug("Successfully stopped daemon %s .", str(daemonModel))
            return True
        else:
            cls.logger.debug("Did not stop daemon %s, it was not running.", str(daemonModel))
            return False
