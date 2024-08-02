import mysql.connector
import logging

class EMailDBFeeder:
    __INSERT_EMAIL_SQL = '''
        INSERT INTO emails (Sender, Recipient, Cc, Bcc, DateReceived, BodyText)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''

    def __init__(self, host, user, password, database, charset, collation):
        try:
            self.__dbConnection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database,
                charset=charset,
                collation=collation
            )
            self.__dbCursor = self.__dbConnection.cursor()

        except mysql.connector.Error as e:
            logging.critical(e.with_traceback())


    def insert(self, parsedEMail):
        emailData = []
        emailData.append(parsedEMail.parseFrom()[0])
        emailData.append(parsedEMail.parseTo()[0][0])
        emailData.append(parsedEMail.parseCc()[0][0])
        emailData.append(parsedEMail.parseBcc()[0][0])
        emailData.append(parsedEMail.parseDate())
        emailData.append(parsedEMail.parseBody())

        try:
            self.__dbCursor.execute(EMailDBFeeder.__INSERT_EMAIL_SQL, emailData)
            self.__dbConnection.commit()
        except Exception as e:
            print(e)

        

    def __del__(self):
        self.__dbCursor.close()
        self.__dbConnection.close()
        