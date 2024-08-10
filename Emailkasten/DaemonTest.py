import logging

from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from POP3_SSL_Fetcher import POP3_SSL_Fetcher
from MailParser import MailParser
from DBManager import DBManager
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