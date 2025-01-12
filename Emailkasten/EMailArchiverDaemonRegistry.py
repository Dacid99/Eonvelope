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

from .Models.DaemonModel import DaemonModel
from .EMailArchiverDaemon import EMailArchiverDaemon


class EMailArchiverDaemonRegistry:
    """Daemon registry for managment of the running :class:`Emailkasten.EMailArchiverDaemon.EMailArchiverDaemon`s."""

    _runningDaemons: dict = {}
    """A static dictionary of all active daemon instances with their database IDs as keys."""

    @classmethod
    def isRunning(cls, daemonModel: DaemonModel) -> bool:
        return daemonModel.id in cls._runningDaemons

    @classmethod
    def updateDaemon(cls, daemonModel: DaemonModel):
        if cls.isRunning(daemonModel):
            daemonInstance = cls._running_daemons[daemonModel.id]
            daemonInstance.update()
            daemonInstance.logger.debug('Daemon updated')

    @classmethod
    def testDaemon(cls, daemonModel: DaemonModel) -> bool:
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


    @classmethod
    def startDaemon(cls, daemonModel: DaemonModel) -> bool:
        """Static method to create, start and add a new daemon to :attr:`runningDaemons`.
        If it is already in the dict does nothing.

        Args:
            daemonModel: The data for the daemon.

        Returns:
            `True` if the daemon was started, `False` if it was already running.
        """
        if not cls.isRunning(daemonModel):
            newDaemon = EMailArchiverDaemon(daemonModel)
            newDaemon.start()
            cls._runningDaemons[daemonModel.id] = newDaemon
            return True
        else:
            return False


    @classmethod
    def stopDaemon(cls, daemonModel: DaemonModel) -> bool:
        """Static method to stop and remove a daemon from :attr:`runningDaemons`.
        If it is not in the dict does nothing.

        Args:
            daemonModel: The data of the daemon.

        Returns:
            `True` if the daemon was stopped, `False` if it wasnt running.
        """
        if cls.isRunning(daemonModel):
            daemon = cls._runningDaemons.pop(daemonModel.id)
            try:
                daemon.stop()
            except RuntimeError:
                daemon.logger.error("Daemon was already stopped!", exc_info=True)
            return True
        else:
            return False
