import mysql.connector
import logging
import traceback

from LoggerFactory import LoggerFactory
from DBManager import DBManager

class EMailDBFeeder:

    MENTION_FROM = "FROM"
    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"


    def __init__(self, dbManager):
        self.__dbManager = dbManager
        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

    def insertEmail(self, parsedEMail):
        emailData = []
        emailData.append(parsedEMail.messageID)
        emailData.append(parsedEMail.dateReceived)
        emailData.append(parsedEMail.bodyText)
        emailData.append(parsedEMail.emlFilePath)

        self.logger.debug("Inserting mail data into emails table ...")
        self.__dbManager.callproc(DBManager.INSERT_EMAIL_PROCEDURE, emailData)
        self.logger.debug("Success")


    def insertCorrespondents(self, parsedEMail):

        if parsedEMail.hasFrom():
            fromCorrespondent = parsedEMail.emailFrom
            self.logger.debug("Inserting FROM correspondents into correspondents table ...")
            self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, fromCorrespondent)
            self.logger.debug("Success")
        else:
            self.logger.warn(f"No FROM correspondent in mail\n{str(parsedEMail)}\nto insert into correspondents table!")

        
        if parsedEMail.hasTo():
            toCorrespondents = parsedEMail.emailTo
            self.logger.debug("Inserting TO correspondents into correspondents table ...")
            for toCorrespondent in toCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, toCorrespondent)
            self.logger.debug("Success")
        else:
            self.logger.warn(f"No TO correspondents in mail\n{str(parsedEMail)}\nto insert into correspondents table!")
        
        if parsedEMail.hasCc():
            ccCorrespondents = parsedEMail.emailCc
            self.logger.debug("Inserting CC correspondents into correspondents table ...")
            for ccCorrespondent in ccCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, ccCorrespondent)
            self.logger.debug("Success")
        else:
            self.logger.debug("No CC correspondents to insert into correspondents table")

        if parsedEMail.hasBcc():
            bccCorrespondents = parsedEMail.emailBcc
            self.logger.debug("Inserting BCC correspondents into correspondents table ...")
            for bccCorrespondent in bccCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, bccCorrespondent)
            self.logger.debug("Success")
        else:
            self.logger.debug("No BCC correspondents to insert into correspondents table")


    def insertEmailCorrespondentsConnection(self, parsedEMail, emailID):

        emailMessageID = parsedEMail.messageID
        
        if parsedEMail.hasFrom():
            fromCorrespondentAddress = parsedEMail.emailFrom[1]

            self.logger.debug("Inserting FROM correspondents of this mail into email_correspondents table ...")

            self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, fromCorrespondentAddress, EMailDBFeeder.MENTION_FROM])
            
            self.logger.debug("Success")
        else:
            self.logger.warn("No FROM correspondents for mail to insert into email_correspondents table!")


        if parsedEMail.hasTo():
            toCorrespondentsAddresses = []

            self.logger.debug("Inserting FROM correspondents of this mail into email_correspondents table ...")

            for toCorrespondent in parsedEMail.emailTo:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, toCorrespondent[1], EMailDBFeeder.MENTION_TO])

            self.logger.debug("Success")
        else:
            self.logger.warn("No FROM correspondents for mail to insert into email_correspondents table!")

        if parsedEMail.hasCc():   
            ccCorrespondentsAddresses = []

            self.logger.debug("Inserting CC correspondents of this mail into email_correspondents table ...")

            for ccCorrespondent in parsedEMail.emailCc:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, ccCorrespondent[1], EMailDBFeeder.MENTION_CC))

            self.logger.debug("Success")
        else:
            self.logger.debug("No CC correspondents for this mail to insert into email_correspondents table")

        if parsedEMail.hasBcc():
            bccCorrespondentsAddresses = []

            self.logger.debug("Inserting BCC correspondents of this mail into email_correspondents table ...")

            for bccCorrespondent in parsedEMail.emailBcc:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, bccCorrespondent[1], EMailDBFeeder.MENTION_BCC))

            self.logger.debug("Success")
        else:
            self.logger.debug("No BCC correspondents for this mail to insert into email_correspondents table")


    def insertAttachments(self, parsedEMail):

        if parsedEMail.hasAttachments():
            self.logger.debug("Inserting attachments into attachments table ...")
            for attachment in parsedEMail.attachmentsFiles:
                attachmentInput = list(attachment)
                attachmentInput.append(parsedEMail.messageID)
                self.__dbManager.callproc(DBManager.INSERT_ATTACHMENT_PROCEDURE, attachmentInput)
            self.logger.debug("Success")
        else:
            self.logger.debug(f"No attachments for this mail to insert into attachments table!")


    def insert(self, parsedEMail):
        try:
            self.__dbManager.startTransaction()

            self.logger.debug(f"Inserting mail\n{str(parsedEMail)}\n into database ...")

            emailID = self.insertEmail(parsedEMail)
            self.insertCorrespondents(parsedEMail)
            self.insertEmailCorrespondentsConnection(parsedEMail, emailID)
            self.insertAttachments(parsedEMail)
            self.__dbManager.commit()

            self.logger.debug("Success")

        except Exception as e:
            self.logger.error(f"Error while writing mail\n{str(parsedEMail)}\n to database! Rolling back uncommitted changes!", exc_info=True)
            self.__dbManager.rollback()



        