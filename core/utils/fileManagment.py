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


"""Provides functions for saving various files to the storage.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import logging
import os.path
import re
from builtins import open  # required for testing
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any


logger = logging.getLogger(__name__)


def saveStore(storingFunc: Callable) -> Callable:
    """Decorator to ensure no files are overwriten and errors are handled when storing files.

    Todo:
        Needs a test that doesnt require workarounds, eg using tempfile

    Args:
        storingFunc: The function writing a file into the storage to wrap.

    Returns:
        saveStoringFunc: The wrapped function.
    """

    def saveStoringFunc(filePath: str, *args: Any, **kwargs: Any) -> str | None:
        if os.path.exists(filePath):
            try:
                if os.path.getsize(filePath) > 0:
                    logger.debug(
                        "Not writing to file %s, it already exists and is not empty.",
                        filePath,
                    )
                    return filePath
            except PermissionError:
                pass  # this is only relevant for fakefs testing
            logger.debug(
                "Writing to file %s, it already exists but is empty.", filePath
            )
        else:
            logger.debug("Creating and writing to file %s...", filePath)

        try:
            with open(filePath, "wb") as file:
                storingFunc(file, *args, **kwargs)
        except PermissionError:
            logger.exception(
                "Failed to write to file %s, it is not writeable!",
                filePath,
            )
            return None
        except Exception:
            logger.exception("Failed to write to file %s!", filePath)
            if os.path.exists(filePath):
                logger.debug("Clearing incomplete file ...")
                try:
                    with open(filePath, "wb") as file:
                        file.truncate(0)

                    logger.debug("Successfully cleared incomplete file.")

                except OSError:
                    logger.exception("Failed to clear the incomplete file!")
            else:
                logger.debug("File was not created")
            return None
        else:
            logger.debug("Successfully wrote to file.")
            return filePath

    return saveStoringFunc


def clean_filename(filename: str) -> str:
    r"""Sanitizes dangerous chars and strips whitespace from a filename.

    Chars /, ., ~ are replaced with _.

    Args:
        The filename without extension.

    Returns:
        The cleaned filename without extension.
    """
    clean_filename = re.sub(r"[/\.~]", "_", filename)
    return re.sub(r"\s+", "", clean_filename).strip()
