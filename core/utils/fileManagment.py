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
Functions starting with _ are helpers and are used only within the scope of this module.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""
from __future__ import annotations

import logging
import os.path
from builtins import open  # required for testing
from typing import TYPE_CHECKING

from Emailkasten.utils import get_config

from ..constants import HeaderFields
from ..models.StorageModel import StorageModel

if TYPE_CHECKING:
    from typing import Any, Callable


logger = logging.getLogger(__name__)


def saveStore(storingFunc: Callable) -> Callable:
    """Decorator to ensure no files are overwriten and errors are handled when storing files.

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

            logger.debug("Successfully wrote to file.")
            return filePath

        except PermissionError:
            logger.error(
                "Failed to write to file %s, it is not writeable!",
                filePath,
                exc_info=True,
            )
            return None
        except OSError:
            logger.error("Failed to write to file %s!", filePath, exc_info=True)
            if os.path.exists(filePath):
                logger.debug("Clearing incomplete file ...")
                try:
                    with open(filePath, "wb") as file:
                        file.truncate(0)

                    logger.debug("Successfully cleared incomplete file.")

                except OSError:
                    logger.error("Failed to clear the incomplete file!")
            else:
                logger.debug("File was not created")
            return None

    return saveStoringFunc


def getPrerenderImageStoragePath(parsedMail: dict[str, Any]) -> str:
    """Gets the storage path for a prerender image.

    Args:
        parsedMail: The parsed mail to be prerendered.

    Returns:
        The path in the storage where the prerender image should be saved.
    """
    logger.debug("Getting storage path for prerender image ...")
    dirPath = StorageModel.getSubdirectory(parsedMail[HeaderFields.MESSAGE_ID])

    filePath = os.path.join(
        dirPath,
        f"{parsedMail[HeaderFields.MESSAGE_ID]}.{get_config('PRERENDER_IMAGETYPE')}",
    )
    parsedMail[""] = filePath
    logger.debug("Successfully got storage path for prerender image.")

    return filePath
