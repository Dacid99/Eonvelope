# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
from typing import TYPE_CHECKING

from .constants import StorageConfiguration
from .mailParsing import ParsedMailKeys
from .Models.StorageModel import StorageModel

if TYPE_CHECKING:
    from typing import Any


logger = logging.getLogger(__name__)


def storeMessageAsEML(parsedEMail: dict[str,Any]) -> None:
    """Saves an entire mail as a .eml file in the storage.
    The files name is given by the unique messageID.
    If the file already exists, does not overwrite. If an error occurs, removes the incomplete file.

    Args:
        parsedEMail: The parsed mail to be saved.

    """
    emlDirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    emlFilePath = os.path.join(emlDirPath , parsedEMail[ParsedMailKeys.Header.MESSAGE_ID] + ".eml")

    logger.debug("Storing mail in .eml file %s ...", emlFilePath)
    try:
        if os.path.exists(emlFilePath):
            if os.path.getsize(emlFilePath) > 0:
                logger.debug("Not writing to %s, it already exists and is not empty", emlFilePath)

            else:
                logger.debug("Writing to empty .eml file %s ...", emlFilePath)

                with open(emlFilePath, "wb") as emlFile:
                    emlGenerator = email.generator.BytesGenerator(emlFile)
                    emlGenerator.flatten(parsedEMail[ParsedMailKeys.FULL_MESSAGE])

                logger.debug("Successfully wrote to empty .eml file.")
        else:
            logger.debug("Creating and writing new .eml file %s...", emlFilePath)

            with open(emlFilePath, "wb") as emlFile:
                emlGenerator = email.generator.BytesGenerator(emlFile)
                emlGenerator.flatten(parsedEMail[ParsedMailKeys.FULL_MESSAGE])

            logger.debug("Successfully created and wrote new .eml file.")

    except OSError:
        logger.error("Failed to write .eml file for message!", exc_info=True)
        if os.path.exists(emlFilePath):
            logger.debug("Clearing incomplete file ...")
            try:
                with open(emlFilePath, "wb") as file:
                    file.truncate(0)

                logger.debug("Successfully cleared incomplete file.")

            except OSError:
                logger.error("Failed to clear the incomplete file!")
        else:
            logger.debug("File was not created")
        emlFilePath = None

    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = emlFilePath
    logger.debug("Successfully stored mail in .eml file.")



def storeAttachments(parsedEMail: dict[str,Any]) -> None:
    """Saves all attachments of a mail to the storage.
    If the file already exists, does not overwrite. If no attachments are found, does nothing. If an error occurs, removes the incomplete file.

    Args:
        parsedEMail: The parsed mail with attachments to be saved.

    """
    logger.debug("Saving attachments from mail ...")

    dirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for attachmentData in parsedEMail[ParsedMailKeys.ATTACHMENTS]:
        fileName = attachmentData[ParsedMailKeys.Attachment.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)

        logger.debug("Storing attachment %s in %s ...", fileName, filePath)
        try:
            if os.path.exists(filePath):
                if os.path.getsize(filePath) > 0:
                    logger.debug("Not writing to %s, it already exists and is not empty", filePath)

                else:
                    logger.debug("Writing to empty file %s ...", filePath)

                    with open(filePath, "wb") as file:
                        file.write(attachmentData[ParsedMailKeys.Attachment.DATA].get_payload(decode=True))

                    logger.debug("Successfully wrote to empty .eml file.")
            else:
                logger.debug("Creating and writing new file %s ...", filePath)

                with open(filePath, "wb") as file:
                    file.write(attachmentData[ParsedMailKeys.Attachment.DATA].get_payload(decode=True))

                logger.debug("Successfully created and wrote new .eml file.")

        except OSError:
            logger.error("Failed to write attachment file %s to %s!", fileName,  filePath, exc_info=True)
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
            filePath = None

        attachmentData[ParsedMailKeys.Attachment.FILE_PATH] = filePath
        logger.debug("Successfully stored attachment.")

    if not parsedEMail[ParsedMailKeys.ATTACHMENTS]:
        logger.debug("No attachments in mail.")
    else:
        logger.debug("Successfully saved attachments to file.")



def storeImages(parsedEMail: dict[str,Any]) -> None:
    """Saves all inline images of a mail to the storage.
    If the file already exists, does not overwrite. If no images are found, does nothing. If an error occurs, removes the incomplete file.

    Args:
        parsedEMail: The parsed mail with inline images to be saved.

    """
    logger.debug("Saving images from mail ...")

    dirPath = StorageModel.getSubdirectory(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for imageData in parsedEMail[ParsedMailKeys.IMAGES]:
        fileName = imageData[ParsedMailKeys.Image.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)

        logger.debug("Storing image %s in %s ...", fileName, filePath)
        try:
            if os.path.exists(filePath):
                if os.path.getsize(filePath) > 0:
                    logger.debug("Not writing to %s, it already exists and is not empty", filePath)

                else:
                    logger.debug("Writing to empty file %s ...", filePath)
                    with open(filePath, "wb") as file:
                        file.write(imageData[ParsedMailKeys.Image.DATA].get_payload(decode=True))
                    logger.debug("Successfully wrote to empty file.")
            else:
                logger.debug("Creating and writing new file %s ...", filePath)

                with open(filePath, "wb") as file:
                    file.write(imageData[ParsedMailKeys.Image.DATA].get_payload(decode=True))

                logger.debug("Successfully created and wrote new file.")

        except OSError:
            logger.error("Failed to write image file %s to %s!", fileName,  filePath, exc_info=True)
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
            filePath = None

        imageData[ParsedMailKeys.Image.FILE_PATH] = filePath
        logger.debug("Successfully stored image.")

    if not parsedEMail[ParsedMailKeys.IMAGES]:
        logger.debug("No images in mail.")
    else:
        logger.debug("Successfully saved images to file.")



def getPrerenderImageStoragePath(parsedMail: dict[str,Any]) -> str:
    """Gets the storage path for a prerender image.

    Args:
        parsedMail: The parsed mail to be prerendered.

    Returns:
        The path in the storage where the prerender image should be saved.
    """
    dirPath = StorageModel.getSubdirectory(parsedMail[ParsedMailKeys.Header.MESSAGE_ID])

    filePath = os.path.join(dirPath, f"{parsedMail[ParsedMailKeys.Header.MESSAGE_ID]}.{StorageConfiguration.PRERENDER_IMAGETYPE}")
    parsedMail[ParsedMailKeys.PRERENDER_FILE_PATH] = filePath
    return filePath
