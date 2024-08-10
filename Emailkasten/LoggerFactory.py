import logging
import logging.handlers

class LoggerFactory:
    loggerName = "EMailArchiverDaemon"
    logfilePath = f"/var/log/{loggerName}.log"
    logLevel = logging.INFO
    logfileMaxSize = 10 * 1024 * 1024 # 10 MB
    logfileBackupCount = 3 
    consoleLogging = False
    logFormat = '%(name)s - %(levelname)s: %(message)s'

    @staticmethod
    def getMainLogger():
        logger = logging.getLogger(LoggerFactory.loggerName)
        logger.setLevel(logging.DEBUG)

        logfileHandler= logging.handlers.RotatingFileHandler(LoggerFactory.logfilePath, maxBytes = LoggerFactory.logfileMaxSize, backupCount = LoggerFactory.logfileBackupCount)
        logfileHandler.setLevel(LoggerFactory.logLevel)
        
        formatter = logging.Formatter(LoggerFactory.logFormat)
        logfileHandler.setFormatter(formatter)
        
        logger.addHandler(logfileHandler)

        if LoggerFactory.consoleLogging:
            consoleHandler = logging.StreamHandler()
            consoleHandler.setLevel(LoggerFactory.logLevel)
            consoleHandler.setFormatter(formatter)
            logger.addHandler(consoleHandler)

        return logger

    
    @staticmethod
    def getChildLogger(instanceName):
        logger = logging.getLogger(LoggerFactory.loggerName + "." + str(instanceName))

        return logger