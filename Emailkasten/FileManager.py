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
from . import constants
import logging
from .MailParsing import ParsedMailKeys

class FileManager:
    subdirNumber = 0
    dirNumber = 0

    @staticmethod
    def writeMessageToEML(parsedEMail):
        logger = logging.getLogger(__name__)
        logger.debug("Storing mail in .eml file ...")
        emlDirPath = FileManager.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
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
                    FileManager.subdirNumber += 1
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


    @staticmethod
    def writeAttachments(parsedEMail):
        logger = logging.getLogger(__name__)

        dirPath = FileManager.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
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
                        FileManager.subdirNumber += 1
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
            
    @staticmethod
    def writeImages(parsedEMail):
        logger = logging.getLogger(__name__)

        dirPath = FileManager.getStoragePath(parsedEMail[ParsedMailKeys.Header.MESSAGE_ID])
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
                        FileManager.subdirNumber += 1
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
            

    @staticmethod
    def getPrerenderImageStoragePath(parsedMail):
        dirPath = FileManager.getStoragePath(parsedMail[ParsedMailKeys.Header.MESSAGE_ID])

        filePath = os.path.join(dirPath, f"{parsedMail[ParsedMailKeys.Header.MESSAGE_ID]}.{constants.StorageConfiguration.PRERENDER_IMAGETYPE}")
        parsedMail[ParsedMailKeys.PRERENDER_FILE_PATH] = filePath
        return filePath

    @staticmethod
    def getStoragePath(filename):
        if FileManager.subdirNumber > constants.StorageConfiguration.MAX_SUBDIRS_PER_DIR:
            FileManager.dirNumber += 1
            FileManager.subdirNumber = 0
        else:
            FileManager.subdirNumber += 1
        path = os.path.join(constants.StorageConfiguration.STORAGE_PATH, str(FileManager.dirNumber), filename)
        return path
            
