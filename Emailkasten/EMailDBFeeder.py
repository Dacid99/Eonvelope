import mysql.connector
import logging
import traceback

from .LoggerFactory import LoggerFactory
from .DBManager import DBManager
from Models.EMailModel import EMailModel
from Models.AttachmentModel import AttachmentModel
from Models.CorrespondentModel import CorrespondentModel
from Models.EMailCorrespondentsModel import EMailCorrespondentsModel


class EMailDBFeeder:

    __MENTION_FROM = "FROM"
    __MENTION_TO = "TO"
    __MENTION_CC = "CC"
    __MENTION_BCC = "BCC"


    def __init__(self, dbManager):
        self.__dbManager = dbManager
        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)

    def insertEmail(self, parsedEMail):
        self.logger.debug("Inserting mail data into emails table ...")
        EMailModel.objects.get_or_create()
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

            self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, fromCorrespondentAddress, EMailDBFeeder.__MENTION_FROM])
            
            self.logger.debug("Success")
        else:
            self.logger.warn("No FROM correspondents for mail to insert into email_correspondents table!")


        if parsedEMail.hasTo():

            self.logger.debug("Inserting TO correspondents of this mail into email_correspondents table ...")

            for toCorrespondent in parsedEMail.emailTo:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, toCorrespondent[1], EMailDBFeeder.__MENTION_TO])

            self.logger.debug("Success")
        else:
            self.logger.warn("No FROM correspondents for mail to insert into email_correspondents table!")

        if parsedEMail.hasCc():   

            self.logger.debug("Inserting CC correspondents of this mail into email_correspondents table ...")

            for ccCorrespondent in parsedEMail.emailCc:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, ccCorrespondent[1], EMailDBFeeder.__MENTION_CC))

            self.logger.debug("Success")
        else:
            self.logger.debug("No CC correspondents for this mail to insert into email_correspondents table")

        if parsedEMail.hasBcc():

            self.logger.debug("Inserting BCC correspondents of this mail into email_correspondents table ...")

            for bccCorrespondent in parsedEMail.emailBcc:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, bccCorrespondent[1], EMailDBFeeder.__MENTION_BCC))

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
            with transaction.atomic():
                emailEntry = EMailModel.get_or_create(
                    message_id = mail.messageID,
                    defaults = {
                        'date_received' : mail.dateReceived,
                        'email_subject' : mail.subject,
                        'bodytext' : mail.bodyText,
                        'datasize' :  mail.dataSize,
                        'eml_filepath' : mail.emlFilePath
                    }
                )

                for attachmentFile in mail.attachmentsFiles:
                    attachmentEntry = AttachmentModel.objects.get_or_create(
                        file_name = attachmentsFiles[0],
                        file_path = attachmentsFiles[1],
                        datasize = attachmentFile[2],
                        email = emailEntry
                    )

                for correspondent in mail.emailFrom():
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondent.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_FROM
                    )

                for correspondent in mail.emailTo():
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondent.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_TO
                    )
                
                for correspondent in mail.emailCc():
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondent.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_CC
                    )

                for correspondent in mail.emailBcc():
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondent.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_BCC
                    )

        except django.db.IntegrityError as e:
            self.logger.error("Error while writing to database, rollback to last state", exc_info=True)


