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

import email
import email.generator
import logging
import os.path
from builtins import open  # required for testing
from typing import TYPE_CHECKING

from Emailkasten.utils import get_config

from ..models.StorageModel import StorageModel
from .mailParsing import ParsedMailKeys

if TYPE_CHECKING:
    from io import BufferedWriter
    from typing import Any, Callable


logger = logging.getLogger(__name__)


def _saveStore(storingFunc: Callable) -> Callable:
    """Decorator to ensure no files are overwriten and errors are handled when storing files.

    Args:
        storingFunc: The function writing a file into the storage to wrap.

    Returns:
        saveStoringFunc: The wrapped function.
    """
    def saveStoringFunc(filePath: str, *args: Any, **kwargs: Any) -> str|None:
        if os.path.exists(filePath):
            try:
                if os.path.getsize(filePath) > 0:
                    logger.debug("Not writing to file %s, it already exists and is not empty.", filePath)
                    return filePath
            except PermissionError:
                pass  # this is only relevant for fakefs testing
            logger.debug("Writing to file %s, it already exists but is empty.", filePath)
        else:
            logger.debug("Creating and writing to file %s...", filePath)

        try:
            with open(filePath, "wb") as file:
                storingFunc(file, *args, **kwargs)

            logger.debug("Successfully wrote to file.")
            return filePath

        except PermissionError:
            logger.error("Failed to write to file %s, it is not writeable!", filePath, exc_info=True)
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


def storeMessageAsEML(parsedEMail: dict[str,Any]) -> None:
    """Saves an entire mail as a .eml file in the storage.
    The files name is given by the unique messageID.
    If the file already exists, does not overwrite. If an error occurs, removes the incomplete file.

    Args:
        parsedEMail: The parsed mail to be saved.
    """
    @_saveStore
    def writeMessageToEML(emlFile: BufferedWriter) -> None:
        emlGenerator = email.generator.BytesGenerator(emlFile)
        emlGenerator.flatten(parsedEMail[ParsedMailKeys.FULL_MESSAGE])

    logger.debug("Saving mail in .eml format.")

    emlDirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    emlFilePath = os.path.join(emlDirPath, parsedEMail[ParsedMailKeys.Header.MESSAGE_ID] + ".eml")
    logger.debug("Storing mail in .eml file %s ...", emlFilePath)

    storageFilePath = writeMessageToEML(emlFilePath)
    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = storageFilePath

    if not storageFilePath:
        logger.debug("Successfully saved mail in .eml format.")
    else:
        logger.debug("Saved mail in .eml format with error.")


def storeAttachments(parsedEMail: dict[str,Any]) -> None:
    """Saves all attachments of a mail to the storage.
    If the file already exists, does not overwrite.
    If no attachments are found, does nothing.
    If an error occurs, removes the incomplete file.

    Args:
        parsedEMail: The parsed mail with attachments to be saved.
    """
    @_saveStore
    def writeAttachment(file: BufferedWriter, attachmentData: dict) -> None:
        file.write(attachmentData[ParsedMailKeys.Attachment.DATA].get_payload(decode=True))

    logger.debug("Saving attachments from mail ...")

    if not parsedEMail[ParsedMailKeys.ATTACHMENTS]:
        logger.debug("No attachments in mail.")
        return

    status = True
    dirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for attachmentData in parsedEMail[ParsedMailKeys.ATTACHMENTS]:
        fileName = attachmentData[ParsedMailKeys.Attachment.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)

        logger.debug("Storing attachment %s in %s ...", fileName, filePath)
        storageFilePath = writeAttachment(filePath, attachmentData)
        if not storageFilePath:
            status = False
        attachmentData[ParsedMailKeys.Attachment.FILE_PATH] = storageFilePath
        logger.debug("Successfully stored attachment.")

    if status:
        logger.debug("Successfully saved images to file.")
    else:
        logger.debug("Saved images to file with error.")


def storeImages(parsedEMail: dict[str,Any]) -> None:
    """Saves all inline images of a mail to the storage.
    If the file already exists, does not overwrite.
    If no images are found, does nothing.
    If an error occurs, removes the incomplete file.

    Note:
        This function only differs from :func:`storeAttachments` by the log messages.

    Args:
        parsedEMail: The parsed mail with inline images to be saved.
    """
    @_saveStore
    def writeImage(file: BufferedWriter, imageData: dict) -> None:
        file.write(imageData[ParsedMailKeys.Image.DATA].get_payload(decode=True))

    logger.debug("Saving images from mail ...")

    if not parsedEMail[ParsedMailKeys.IMAGES]:
        logger.debug("No images in mail.")
        return

    status = True
    dirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for imageData in parsedEMail[ParsedMailKeys.IMAGES]:
        fileName = imageData[ParsedMailKeys.Image.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)

        logger.debug("Storing image %s in %s ...", fileName, filePath)
        storageFilePath = writeImage(filePath, imageData)
        if not storageFilePath:
            status = False
        imageData[ParsedMailKeys.Image.FILE_PATH] = storageFilePath
        logger.debug("Successfully stored image.")

    if status:
        logger.debug("Successfully saved images to file.")
    else:
        logger.debug("Saved images to file with error.")


def getPrerenderImageStoragePath(parsedMail: dict[str,Any]) -> str:
    """Gets the storage path for a prerender image.

    Args:
        parsedMail: The parsed mail to be prerendered.

    Returns:
        The path in the storage where the prerender image should be saved.
    """
    logger.debug("Getting storage path for prerender image ...")
    dirPath = StorageModel.getSubdirectory(parsedMail[ParsedMailKeys.Header.MESSAGE_ID])

    filePath = os.path.join(
        dirPath,
        f"{parsedMail[ParsedMailKeys.Header.MESSAGE_ID]}.{get_config('PRERENDER_IMAGETYPE')}",
    )
    parsedMail[ParsedMailKeys.PRERENDER_FILE_PATH] = filePath
    logger.debug("Successfully got storage path for prerender image.")

    return filePath
