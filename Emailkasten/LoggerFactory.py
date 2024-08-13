import logging
import logging.handlers
import os.environ 

class LoggerFactory:
    loggerName = "EMailkasten"
    logfilePath = f"/var/log/{loggerName}.log"
    logLevel = os.environ.get('LOG_LEVEL', 'INFO')
    logfileMaxSize = 10 * 1024 * 1024 # 10 MB
    logfileBackupCount = 3 
    consoleLogging = False
    logFormat = '{name} {levelname} {asctime} {module} {message}'

    @staticmethod
    def getMainLogger():
        logger = logging.getLogger(LoggerFactory.loggerName)
        
        return logger

    
    @staticmethod
    def getChildLogger(instanceName):
        logger = logging.getLogger(LoggerFactory.loggerName + "." + str(instanceName))

        return logger