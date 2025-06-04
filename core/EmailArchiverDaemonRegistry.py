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

"""Module with the :class:`EmailArchiverDaemonRegistry` class."""

from __future__ import annotations

import logging
from typing import ClassVar

from .EmailArchiverDaemon import EmailArchiverDaemon
from .models import Daemon


class EmailArchiverDaemonRegistry:
    """Daemon registry for management of the running :class:`core.EmailArchiverDaemon.EmailArchiverDaemon` instances."""

    _running_daemons: ClassVar[dict[int, EmailArchiverDaemon]] = {}
    """A static dictionary of all active daemon instances with their database IDs as keys."""

    logger: logging.Logger = logging.getLogger(__name__)
    """The logger instance for this singleton."""

    @classmethod
    def is_running(cls, daemon: Daemon) -> bool:
        """Class method to check whether a daemon is active.

        Args:
            daemon: The data for the daemon to check.

        Returns:
            Whether the daemon is active.
        """
        return daemon.id in cls._running_daemons

    @classmethod
    def update_daemon(cls, daemon: Daemon) -> None:
        """Class method to update a daemon instance.

        Args:
            daemon: The data for the daemon to update.
        """
        if cls.is_running(daemon):
            daemon_instance = cls._running_daemons[daemon.id]
            daemon_instance.update()
            cls.logger.debug("Updated daemon %s", daemon)

    @classmethod
    def test_daemon(cls, daemon: Daemon) -> bool:
        """Class method to test data for a daemon.

        Args:
            daemon: The data for the daemon to be tested.

        Returns:
            Whether the test was successful.
        """
        try:
            new_daemon_instance = EmailArchiverDaemon(daemon)
            cls.logger.debug("Testing daemon %s ...", daemon)
            new_daemon_instance.cycle()
        except Exception:
            cls.logger.exception("Test for daemon %s failed!", daemon)
            daemon.is_healthy = False
            daemon.save(update_fields=["is_healthy"])
            return False
        else:
            cls.logger.debug("Successfully tested daemon %s.", daemon)
            return True

    @classmethod
    def start_daemon(cls, daemon: Daemon) -> bool:
        """Class method to create, start and add a new daemon to :attr:`_running_daemons`.

        Args:
            daemon: The data for the daemon.

        Returns:
            `True` if the daemon was started, `False` if it was already running.
        """
        if not cls.is_running(daemon):
            cls.logger.debug("Starting daemon %s ...", daemon)
            new_daemon_instance = EmailArchiverDaemon(daemon)
            new_daemon_instance.start()
            cls._running_daemons[daemon.id] = new_daemon_instance
            cls.logger.debug("Successfully started daemon %s .", daemon)
            return True
        cls.logger.debug("Did not start daemon %s, it was already running.", daemon)
        return False

    @classmethod
    def stop_daemon(cls, daemon: Daemon) -> bool:
        """Class method to stop and remove a daemon from :attr:`_running_daemons`.

        Args:
            daemon: The data of the daemon.

        Returns:
            `True` if the daemon was stopped, `False` if it wasn't running.
        """
        if cls.is_running(daemon):
            cls.logger.debug("Stopping daemon %s ...", daemon)
            daemon_instance = cls._running_daemons.pop(daemon.id)
            daemon_instance.stop()
            cls.logger.debug("Successfully stopped daemon %s .", daemon)
            return True

        cls.logger.debug("Did not stop daemon %s, it was not running.", daemon)
        return False

    @staticmethod
    def healthcheck() -> bool:
        """Checks whether the :attr:`is_running` flag on every :class:`core.models.Daemon` is correct."""
        return all(
            daemon.is_running is EmailArchiverDaemonRegistry.is_running(daemon)
            for daemon in Daemon.objects.all()
        )
