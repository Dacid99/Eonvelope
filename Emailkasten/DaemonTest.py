import logging

from LoggerFactory import LoggerFactory
from EMailArchiverDaemon import EMailArchiverDaemon
from FileManager import FileManager

# on Windows
FileManager.emlDirectoryPath = "C:\\Users\\phili\\Desktop\\emltest\\"
FileManager.attachmentDirectoryPath = "C:\\Users\\phili\\Desktop\\attachmenttest\\"
LoggerFactory.logfilePath = "C:\\Users\\phili\\Desktop\\log.log\\"


# on Linux
# FileManager.emlDirectoryPath = "/home/david/emltest/"
# FileManager.attachmentDirectoryPath = "/home/david/attachmenttest/"
# LoggerFactory.logfilePath = "/home/david/log.log"

LoggerFactory.logLevel = logging.DEBUG
LoggerFactory.consoleLogging = True



if __name__ == "__main__":
    daemon = EMailArchiverDaemon()
    daemon.start()