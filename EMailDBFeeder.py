import mysql.connector
import logging
import traceback

from DBManager import DBManager

class EMailDBFeeder:

    __SELECT_CORRESPONDENTS_ID_SQL = '''
        SELECT id FROM correspondents WHERE email_address IN (%s)
    '''

    MENTION_FROM = "FROM"
    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"


    def __init__(self, dbManager):
        self.__dbManager = dbManager

    def insertEmail(self, parsedEMail):
        emailData = []
        emailData.append(parsedEMail.messageID)
        emailData.append(parsedEMail.dateReceived)
        emailData.append(parsedEMail.bodyText)
        self.__dbManager.callproc(DBManager.INSERT_EMAIL_PROCEDURE, emailData)

    def insertCorrespondents(self, parsedEMail):

        if parsedEMail.hasFrom():
            fromCorrespondent = parsedEMail.emailFrom
            self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, fromCorrespondent)
        
        if parsedEMail.hasTo():
            toCorrespondents = parsedEMail.emailTo
            for toCorrespondent in toCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, toCorrespondent)
        
        if parsedEMail.hasCc():
            ccCorrespondents = parsedEMail.emailCc
            for ccCorrespondent in ccCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, ccCorrespondent)
        
        if parsedEMail.hasBcc():
            bccCorrespondents = parsedEMail.emailBcc
            for bccCorrespondent in bccCorrespondents:
                self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, bccCorrespondent)


    def insertEmailCorrespondentsConnection(self, parsedEMail, emailID):

        emailMessageID = parsedEMail.messageID
        fromCorrespondentAddress = parsedEMail.emailFrom[1]

        toCorrespondentsAddresses = []
        for toCorrespondent in parsedEMail.emailTo:
            toCorrespondentsAddresses.append(toCorrespondent[1])

        ccCorrespondentsAddresses = []
        for ccCorrespondent in parsedEMail.emailCc:
            ccCorrespondentsAddresses.append(ccCorrespondent[1])

        bccCorrespondentsAddresses = []
        for bccCorrespondent in parsedEMail.emailBcc:
            bccCorrespondentsAddresses.append(bccCorrespondent[1])


        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL, [fromCorrespondentAddress])
        fromCorrespondentID = self.__dbManager.fetchall()

        self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, fromCorrespondentID[0][0], EMailDBFeeder.MENTION_FROM])


        if toCorrespondentsAddresses:  
            self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(toCorrespondentsAddresses)), toCorrespondentsAddresses)
            toCorrespondentsIDs = self.__dbManager.fetchall()

            for toCorrespondentId in toCorrespondentsIDs:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, toCorrespondentId[0], EMailDBFeeder.MENTION_TO])


        if ccCorrespondentsAddresses:        
            self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(ccCorrespondentsAddresses)), ccCorrespondentsAddresses)
            ccCorrespondentsIDs = self.__dbManager.fetchall()
            
            for ccCorrespondentId in ccCorrespondentsIDs:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, ccCorrespondentId[0], EMailDBFeeder.MENTION_CC))


        if bccCorrespondentsAddresses:
            self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(bccCorrespondentsAddresses)), bccCorrespondentsAddresses)
            bccCorrespondentsIDs = self.__dbManager.fetchall()

            for bccCorrespondentId in bccCorrespondentsIDs:
                self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, bccCorrespondentId[0], EMailDBFeeder.MENTION_BCC))



    def insert(self, parsedEMail):
        try:
            self.__dbManager.startTransaction()
            emailID = self.insertEmail(parsedEMail)
            self.insertCorrespondents(parsedEMail)
            self.insertEmailCorrespondentsConnection(parsedEMail, emailID)
            self.__dbManager.commit()
        except Exception as e:
            logging.error("Error while writing to database! Rolling back uncommitted changes!", exc_info=True)
            self.__dbManager.rollback()



        