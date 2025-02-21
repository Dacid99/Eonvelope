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

"""Module with the constant values for the :mod:`Emailkasten` application."""

from __future__ import annotations

import os
from typing import Final


class LoggerConfiguration:
    """Namespace class for all configurations constants for the application loggers."""

    LOG_DIRECTORY_PATH: Final[str] = ""  # /var/log
    """The path to directory with the logs.
    Must match the path in the docker-compose.yml to store the logs outside the container."""

    APP_LOGFILE_NAME: Final[str] = "Emailkasten.log"
    """The name of the Emailkasten logfile."""

    DJANGO_LOGFILE_NAME: Final[str] = "django.log"
    """The name of the django logfile."""

    APP_LOG_LEVEL: Final[str] = os.environ.get("APP_LOG_LEVEL", "INFO")
    """The loglevel to the Emailkasten logfile.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    DJANGO_LOG_LEVEL: Final[str] = os.environ.get("DJANGO_LOG_LEVEL", "INFO")
    """The loglevel to the django logfile.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    ROOT_LOG_LEVEL: Final[str] = os.environ.get("ROOT_LOG_LEVEL", "INFO")
    """The loglevel to the root console logger.
    Is being set from an environment variable of the same name.
    Defaults to INFO."""

    LOGFILE_MAXSIZE: Final[int] = int(
        os.environ.get("LOGFILE_MAXSIZE", 10 * 1024 * 1024)
    )
    """The maximum file size of a logfile.
    Is being set from an environment variable of the same name.
    Defaults to 10 MB.

    Todo:
        The int cast it not safe!"""

    LOGFILE_BACKUP_NUMBER: Final[int] = int(os.environ.get("LOGFILE_BACKUP_NUMBER", 5))
    """The maximum number of backup logfiles to keep.
    Is being set from an environment variable of the same name.
    Defaults to 5.

    Todo:
        The int cast is not safe!"""

    LOG_FORMAT: Final[str] = "{asctime} {levelname} - {name}.{funcName}: {message}"
    """The format of the log messages for all loggers."""


class DatabaseConfiguration:
    """Namespace class for all configurations constants for the database."""

    NAME: Final[str] = os.environ.get("DB_NAME", "emailkasten")
    """The name of the database on the mariadb server. Can be set from docker-compose.yml."""

    USER: Final[str] = os.environ.get("DB_USER", "user")
    """The name of the database user. Can be set from docker-compose.yml."""

    PASSWORD: Final[str] = os.environ.get("DB_PASSWORD", "passwd")
    """The password of the database user. Can be set from docker-compose.yml."""

    RECONNECT_RETRIES: Final[int] = 10
    """The number of reconnect attempt in case of database disconnect."""

    RECONNECT_DELAY: Final[int] = 30
    """The delay between reconnect attempt in case of database disconnect."""
