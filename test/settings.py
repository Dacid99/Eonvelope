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

"""Settings for testing of the django project."""

from __future__ import annotations

import sys
from os import environ
from pathlib import Path

from environ import Env


sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

Env.read_env()
environ["DEBUG"] = "True"

from Emailkasten.settings import *  # noqa: F403,E402 ; pylint: disable=wildcard-import, unused-wildcard-import ; all settings need to be imported and environment needs to be set beforehand


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Use SQLite in memory
        "NAME": ":memory:",
    }
}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "{asctime} {levelname} - {name}.{funcName}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "null": {"class": "logging.NullHandler"},
    },
    "root": {
        "handlers": ["console"],
        "level": "ERROR",
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "level": "ERROR",
            "propagate": True,
        },
        "Emailkasten": {
            "handlers": ["null"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
