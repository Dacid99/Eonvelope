import mysql.connector
import time
from LoggerFactory import LoggerFactory

class DBManager:
    INSERT_EMAIL_PROCEDURE = "safe_insert_email"

    INSERT_CORRESPONDENT_PROCEDURE = "safe_insert_correspondent"

    INSERT_ATTACHMENT_PROCEDURE = "safe_insert_attachment"
    
    INSERT_EMAIL_CORRESPONDENT_CONNECTION_PROCEDURE = "safe_insert_email_correspondent"

    reconnectWaitTime = 15  #seconds

    def __init__(self, host, user, password, database, charset, collation):
        self.host = host
        self.user = user 
        self.password = password
        self.database = database
        self.charset = charset
        self.collation = collation
        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)
        self.logger.info("Initial connecting to database ...")
        try:
            self.connect()
        except mysql.connector.Error as e:
            self.logger.error("Failed to create initial connection to database! Please check the credentials!")
            self.heal()
        self.logger.info("Successfully connected to database")

    def connect(self):
        self.logger.debug(f"Connecting to database {self.database} at {self.host} with user {self.user} and password {self.password} ...")
        self.__dbConnection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            collation=self.collation
        )
        self.__dbCursor = self.__dbConnection.cursor()
        self.logger.debug(f"Successfully connected to database {self.database} at {self.host} with user {self.user} and password {self.password}.")


    def close(self):
        self.logger.debug("Closing connection to database ...")
        if self.__dbConnection and self.__dbConnection.is_connected():
            self.__dbCursor.close()
            self.__dbConnection.close()
            self.logger.info("Connection to database closed gracefully")
        else:
            self.logger.debug("Connection to database is already closed")

    def isHealthy(self):
        return self.__dbConnection.is_connected()

    def withHeal(method):
        def methodWithHeal(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except mysql.connector.Error as e:
                self.logger.error("Database connection error!", exc_info=True)
                self.heal()
                return method(self, *args, **kwargs)
        return methodWithHeal


    def heal(self):
        while not self.__dbConnection.is_connected():
            time.sleep(DBManager.reconnectWaitTime)
            self.logger.error("No connection to database! Attempting reconnect ...")
            try:
                self.connect()
                self.logger.info("Reconnected to database")
            except mysql.connector.Error as e:
                self.logger.error("Reconnect attempt failed!")

    @withHeal
    def execute(self, sqlStatement, values=None):
        self.logger.debug(f"Executing SQL Statement {sqlStatement} with values {values} ...")
        self.__dbCursor.execute(sqlStatement, values)
        self.logger.debug("Success")

    @withHeal
    def callproc(self, procedure, values):
        self.logger.debug(f"Executing SQL Procedure {procedure} with values {values} ...")
        self.__dbCursor.callproc(procedure, values)
        self.logger.debug("Success")



    @withHeal
    def fetchall(self):
        return self.__dbCursor.fetchall()


    @withHeal
    def startTransaction(self):
        self.logger.debug("Starting database transaction ...")
        self.__dbConnection.start_transaction()
        self.logger.debug("Success")


    @withHeal
    def commit(self):
        self.logger.debug("Commiting transaction to database ...")
        self.__dbConnection.commit()
        self.logger.debug("Success")

    @withHeal
    def rollback(self):
        self.logger.debug("Rolling back uncommitted changes to database ...")
        self.__dbConnection.rollback()
        self.logger.debug("Success")
    


                

    def __enter__(self):
        self.logger.debug("DBManager.__enter__")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        self.logger.debug("DBManager.__exit__")


        