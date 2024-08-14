import email
import email.generator
import os.path
import sys
from .LoggerFactory import LoggerFactory

class FileManager:
    subdirNumber = 0
    dirNumber = 0
    maxSubdirsPerDir = 10000
    STORAGE_PATH = "/mnt/archive"
    

    @staticmethod
    def writeMessageToEML(parsedEMail):
        logger = LoggerFactory.getChildLogger(FileManager.__class__.__name__)
        logger.debug("Storing mail in .eml file ...")
        emlDirPath = getStoragePath(parsedEMail[MailParser.messageIDString])
        emlFilePath = os.path.join(emlDirPath , parsedEMail[MailParser.messageIDString] + ".eml")
        try:
            if os.path.exists(emlFilePath):
                if os.path.getsize(emlFilePath) > 0:
                    logger.debug(f"Not writing to {emlFilePath}, it already exists and is not empty")
                    return emlFilePath
                else:
                    logger.debug(f"Writing to empty .eml file {emlFilePath} ...")
                    with open(emlFilePath, "wb") as emlFile:
                        emlGenerator = email.generator.BytesGenerator(emlFile)
                        emlGenerator.flatten(parsedEMail[MailParser.fullMessageString])
                    logger.debug("Success")
            else:
                if not os.path.exists(emlDirPath):
                    logger.debug(f"Creating directory {emlDirPath} ...")
                    os.makedirs(emlDirPath)
                    subdirNumber += 1
                    logger.debug("Success")
                logger.debug(f"Creating and writing new .eml file {emlFilePath}...")
                with open(emlFilePath, "wb") as emlFile:
                    emlGenerator = email.generator.BytesGenerator(emlFile)
                    emlGenerator.flatten(parsedEMail[MailParser.fullMessageString])
                
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

        parsedEMail[FileManager.emlFilePathString] = emlFilePath


    @staticmethod
    def writeAttachments(parsedEMail):
        logger = LoggerFactory.getChildLogger(FileManager.__class__.__name__)

        dirPath = getStoragePath(parsedEMail[MailParser.messageIDString])
        for attachmentData in parsedEMail[MailParser.attachmentDataString]:
            fileName = attachmentData.get_filename()
            filePath = os.path.join(dirPath, fileName)
            logger.debug(f"Storing attachment {fileName} in {filePath} ...")
            try:
                if os.path.exists(filePath):
                    if os.path.getsize(filePath) > 0:
                        logger.debug(f"Not writing to {filePath}, it already exists and is not empty")
                        return (fileName, filePath, fileSize)
                    else:
                        logger.debug(f"Writing to empty file {filePath} ...")
                        with open(filePath, "wb") as file:
                            file.write(attachmentData.get_payload(decode=True))
                        logger.debug("Success")
                else:
                    if not os.path.exists(dirPath):
                        logger.debug(f"Creating directory {dirPath} ...")
                        os.makedirs(dirPath)
                        subdirNumber += 1
                        logger.debug("Success")
                    logger.debug(f"Creating new file {filePath} ...")
                    with open(filePath, "wb") as file:
                        file.write(attachmentData.get_payload(decode=True))
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
        
            parsedEMail[MailParser.attachment_filePathString] = filePath


    @staticmethod
    def getStoragePath(filename):
        if subdirNumber > maxSubdirsPerDir:
            dirNumber += 1
            subdirNumber = 0
        path = os.path.join(STORAGE_PATH, dirNumber, filename)
        return path
            
