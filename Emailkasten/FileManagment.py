'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import email
import email.generator
import os.path
from .constants import StorageConfiguration
import logging
from .MailParsing import ParsedMailKeys

class StorageState:
    subdirNumber = 0
    dirNumber = 0
    
    @staticmethod
    def newSubDir():
        StorageState.subdirNumber += 1
        if (StorageState.subdirNumber >= StorageConfiguration.MAX_SUBDIRS_PER_DIR):
            StorageState.dirNumber += 1
            StorageState.subdirNumber = 0

    @staticmethod
    def getStoragePath(filename):
        path = os.path.join(StorageConfiguration.STORAGE_PATH, str(StorageState.dirNumber), filename)
        return path
            


def writeMessageToEML(parsedEMail):
    logger = logging.getLogger(__name__)
    logger.debug("Storing mail in .eml file ...")
    emlDirPath = StorageState.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    emlFilePath = os.path.join(emlDirPath , parsedEMail[ParsedMailKeys.Header.MESSAGE_ID] + ".eml")
    try:
        if os.path.exists(emlFilePath):
            if os.path.getsize(emlFilePath) > 0:
                logger.debug(f"Not writing to {emlFilePath}, it already exists and is not empty")
                
            else:
                logger.debug(f"Writing to empty .eml file {emlFilePath} ...")
                with open(emlFilePath, "wb") as emlFile:
                    emlGenerator = email.generator.BytesGenerator(emlFile)
                    emlGenerator.flatten(parsedEMail[ParsedMailKeys.FULL_MESSAGE])
                logger.debug("Success")
        else:
            if not os.path.exists(emlDirPath):
                logger.debug(f"Creating directory {emlDirPath} ...")
                os.makedirs(emlDirPath)
                StorageState.newSubDir()
                logger.debug("Success")
            logger.debug(f"Creating and writing new .eml file {emlFilePath}...")
            with open(emlFilePath, "wb") as emlFile:
                emlGenerator = email.generator.BytesGenerator(emlFile)
                emlGenerator.flatten(parsedEMail[ParsedMailKeys.FULL_MESSAGE])
            
            logger.debug("Success")

    except OSError as e:
        logger.error(f"Failed to write .eml file for message!", exc_info=True)
        if os.path.exists(emlFilePath):
            logger.debug("Clearing incomplete file ...")
            try: 
                with open(emlFilePath, "wb") as file:
                    file.truncate(0)
                logger.debug("Success")
            except OSError as e:
                logger.error("Failed to clear the incomplete file!")
        else:
            logger.debug("File was not created")
        emlFilePath = None

    parsedEMail[ParsedMailKeys.EML_FILE_PATH] = emlFilePath



def writeAttachments(parsedEMail):
    logger = logging.getLogger(__name__)

    dirPath = StorageState.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for attachmentData in parsedEMail[ParsedMailKeys.ATTACHMENTS]:
        fileName = attachmentData[ParsedMailKeys.Attachment.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)
        logger.debug(f"Storing attachment {fileName} in {filePath} ...")
        try:
            if os.path.exists(filePath):
                if os.path.getsize(filePath) > 0:
                    logger.debug(f"Not writing to {filePath}, it already exists and is not empty")
                    
                else:
                    logger.debug(f"Writing to empty file {filePath} ...")
                    with open(filePath, "wb") as file:
                        file.write(attachmentData[ParsedMailKeys.Attachment.DATA].get_payload(decode=True))
                    logger.debug("Success")
            else:
                if not os.path.exists(dirPath):
                    logger.debug(f"Creating directory {dirPath} ...")
                    os.makedirs(dirPath)
                    StorageState.newSubDir()
                    logger.debug("Success")
                logger.debug(f"Creating new file {filePath} ...")
                with open(filePath, "wb") as file:
                    file.write(attachmentData[ParsedMailKeys.Attachment.DATA].get_payload(decode=True))
                logger.debug("Success")

        except OSError as e:
            logger.error(f"Failed to write attachment file {fileName} to {filePath}!", exc_info=True)
            if os.path.exists(filePath):
                logger.debug("Clearing incomplete file ...")
                try: 
                    with open(filePath, "wb") as file:
                        file.truncate(0)
                    logger.debug("Success")
                except OSError as e:
                    logger.error("Failed to clear the incomplete file!")
            else:
                logger.debug("File was not created")
            filePath = None
    
        attachmentData[ParsedMailKeys.Attachment.FILE_PATH] = filePath
        


def writeImages(parsedEMail):
    logger = logging.getLogger(__name__)

    dirPath = StorageState.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
    for imageData in parsedEMail[ParsedMailKeys.IMAGES]:
        fileName = imageData[ParsedMailKeys.Image.FILE_NAME]
        filePath = os.path.join(dirPath, fileName)
        logger.debug(f"Storing image {fileName} in {filePath} ...")
        try:
            if os.path.exists(filePath):
                if os.path.getsize(filePath) > 0:
                    logger.debug(f"Not writing to {filePath}, it already exists and is not empty")
                    
                else:
                    logger.debug(f"Writing to empty file {filePath} ...")
                    with open(filePath, "wb") as file:
                        file.write(imageData[ParsedMailKeys.Image.DATA].get_payload(decode=True))
                    logger.debug("Success")
            else:
                if not os.path.exists(dirPath):
                    logger.debug(f"Creating directory {dirPath} ...")
                    os.makedirs(dirPath)
                    StorageState.newSubDir()
                    logger.debug("Success")
                logger.debug(f"Creating new file {filePath} ...")
                with open(filePath, "wb") as file:
                    file.write(imageData[ParsedMailKeys.Image.DATA].get_payload(decode=True))
                logger.debug("Success")

        except OSError as e:
            logger.error(f"Failed to write image file {fileName} to {filePath}!", exc_info=True)
            if os.path.exists(filePath):
                logger.debug("Clearing incomplete file ...")
                try: 
                    with open(filePath, "wb") as file:
                        file.truncate(0)
                    logger.debug("Success")
                except OSError as e:
                    logger.error("Failed to clear the incomplete file!")
            else:
                logger.debug("File was not created")
            filePath = None
    
        imageData[ParsedMailKeys.Image.FILE_PATH] = filePath
        


def getPrerenderImageStoragePath(parsedMail):
    dirPath = StorageState.getStoragePath(parsedMail[ParsedMailKeys.Header.MESSAGE_ID])

    filePath = os.path.join(dirPath, f"{parsedMail[ParsedMailKeys.Header.MESSAGE_ID]}.{StorageConfiguration.PRERENDER_IMAGETYPE}")
    parsedMail[ParsedMailKeys.PRERENDER_FILE_PATH] = filePath
    return filePath

        
