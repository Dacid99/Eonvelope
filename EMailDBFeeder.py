import mysql.connector
import logging
import traceback

from DBManager import DBManager

class EMailDBFeeder:

    __SELECT_CORRESPONDENTS_ID_SQL = '''
        SELECT id FROM correspondents WHERE email_address IN (%s)
    '''

    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"


    def __init__(self, dbManager):
        self.__dbManager = dbManager

    def insertEmail(self, parsedEMail):
        emailData = []
        emailData.append(parsedEMail.parseMessageID())
        emailData.append(parsedEMail.parseFrom()[1])
        emailData.append(parsedEMail.parseDate())
        emailData.append(parsedEMail.parseBody())
        self.__dbManager.callproc(DBManager.INSERT_EMAIL_PROCEDURE, emailData)

    def insertCorrespondents(self, parsedEMail):

        toCorrespondents = parsedEMail.parseTo()
        ccCorrespondents = parsedEMail.parseCc()
        bccCorrespondents = parsedEMail.parseBcc()

        for toCorrespondent in toCorrespondents:
            self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, toCorrespondent)
        for ccCorrespondent in ccCorrespondents:
            self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, ccCorrespondent)
        for bccCorrespondent in bccCorrespondents:
            self.__dbManager.callproc(DBManager.INSERT_CORRESPONDENT_PROCEDURE, bccCorrespondent)


    def insertEmailCorrespondentsConnection(self, parsedEMail, emailID):

        toCorrespondentsAddresses = []
        for toCorrespondent in parsedEMail.parseTo():
            toCorrespondentsAddresses.append(toCorrespondent[1])

        ccCorrespondentsAddresses = []
        for ccCorrespondent in parsedEMail.parseCc():
            ccCorrespondentsAddresses.append(ccCorrespondent[1])

        bccCorrespondentsAddresses = []
        for bccCorrespondent in parsedEMail.parseBcc():
            bccCorrespondentsAddresses.append(bccCorrespondent[1])


        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(toCorrespondentsAddresses)), toCorrespondentsAddresses)
        toCorrespondentsIDs = self.__dbManager.fetchall()
        
        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(ccCorrespondentsAddresses)), ccCorrespondentsAddresses)
        ccCorrespondentsIDs = self.__dbManager.fetchall()
        
        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(bccCorrespondentsAddresses)), bccCorrespondentsAddresses)
        bccCorrespondentsIDs = self.__dbManager.fetchall()

        emailMessageID = parsedEMail.parseMessageID()
        for toCorrespondentId in toCorrespondentsIDs:
            self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, [emailMessageID, toCorrespondentId[0], EMailDBFeeder.MENTION_TO])

        for ccCorrespondentId in ccCorrespondentsIDs:
            self.__dbManager.callproc(DBManager.INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE, (emailMessageID, ccCorrespondentId[0], EMailDBFeeder.MENTION_CC))

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



        