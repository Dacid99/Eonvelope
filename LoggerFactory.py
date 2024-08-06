import logging
import logging.handlers

class LoggerFactory:
    loggerName = "EMailArchiverDaemon"
    logfilePath = f"/var/log/{loggerName}.log"
    logLevel = logging.INFO
    logfileMaxSize = 10 * 1024 * 1024 # 1 MB
    logfileBackupCount = 3 

    @staticmethod
    def getMainLogger():
        logger = logging.getLogger(LoggerFactory.loggerName)
        logger.setLevel(logging.DEBUG)

        logfileHandler= logging.handlers.RotatingFileHandler(LoggerFactory.logfilePath, maxBytes = LoggerFactory.logfileMaxSize, backupCount = LoggerFactory.logfileBackupCount)
        logfileHandler.setLevel(LoggerFactory.logLevel)
        logger.addHandler(logfileHandler)

        return logger

    
    @staticmethod
    def getChildLogger(instanceName):
        logger = logging.getLogger(LoggerFactory.loggerName + "." + str(instanceName))

        return logger