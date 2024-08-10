import logging

from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from POP3_SSL_Fetcher import POP3_SSL_Fetcher
from MailParser import MailParser
from DBManager import DBManager
from LoggerFactory import LoggerFactory
from FileManager import FileManager

# on Windows
MailParser.emlDirectoryPath = "C:\\Users\\phili\\Desktop\\emltest\\"
MailParser.attachmentDirectoryPath = "C:\\Users\\phili\\Desktop\\attachmenttest\\"
LoggerFactory.logfilePath = "C:\\Users\\phili\\Desktop\\log.log\\"

# #on Linux
# FileManager.emlDirectoryPath = "/home/david/emltest/"
# FileManager.attachmentDirectoryPath = "/home/david/attachmenttest/"
# LoggerFactory.logfilePath = "/home/david/log.log"

LoggerFactory.logLevel = logging.DEBUG

LoggerFactory.consoleLogging = True


logger = LoggerFactory.getMainLogger()



with DBManager("192.168.178.109", "root", "example", "email_archive", "utf8mb4", "utf8mb4_bin") as db:

    with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="imap.ionos.de", port=993) as imapMail:
    #with POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as popMail:

        parsedNewMails = imapMail.fetchBySearch(searchCriterion="ALL")
        #parsedNewMails = popMail.fetchAll("")

        dbfeeder = EMailDBFeeder(db)
      
        for mail in parsedNewMails:
            mail.saveAttachments()
            mail.saveToEML()
            dbfeeder.insert(mail)