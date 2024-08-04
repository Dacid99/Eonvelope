import mysql.connector
import time
import logging

class DBManager:
    reconnectWaitTime = 15  #seconds

    def __init__(self, host, user, password, database, charset, collation):
        self.host = host
        self.user = user 
        self.password = password
        self.database = database
        self.charset = charset
        self.collation = collation
        logging.info("Initial connecting to database ...")
        try:
            self.connect()
        except mysql.connector.Error as e:
            logging.error("Failed to create initial connection to database! Please check the credentials!")
            self.heal()
        logging.info("Successfully connected to database")

    def connect(self):
        logging.debug(f"Connecting to database {self.database} at {self.host} with user {self.user} and password {self.password} ...")
        self.__dbConnection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset,
            collation=self.collation
        )
        self.__dbCursor = self.__dbConnection.cursor()
        logging.debug(f"Succesfully connected to database {self.database} at {self.host} with user {self.user} and password {self.password}.")


    def close(self):
        logging.debug("Closing connection to database ...")
        if self.__dbConnection and self.__dbConnection.is_connected():
            self.__dbCursor.close()
            self.__dbConnection.close()
            logging.info("Connection to database closed gracefully")
        else:
            logging.debug("Connection to database is already closed")

    def isHealthy(self):
        return self.__dbConnection.is_connected()

    def withHeal(method):
        def methodWithHeal(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except mysql.connector.Error as e:
                logging.error("Database connection error!", exc_info=True)
                self.heal()
                return method(self, *args, **kwargs)
        return methodWithHeal


    def heal(self):
        while not self.__dbConnection.is_connected():
            time.sleep(DBManager.__reconnectWaitTime)
            logging.error("No connection to database! Attempting reconnect ...")
            try:
                self.connect()
                logging.info("Reconnected to database")
            except sql.connector.Error as e:
                logging.error("Reconnect attempt failed!")

    @withHeal
    def execute(self, sqlStatement, values=None):
        self.__dbCursor.execute(sqlStatement, values)
        logging.debug(f"Executed SQL Statement {sqlStatement} with values {values}")
        return self.__dbCursor.lastrowid

    @withHeal
    def fetchall(self):
        return self.__dbCursor.fetchall()


    @withHeal
    def startTransaction(self):
        self.__dbConnection.start_transaction()
        logging.debug("Database transaction started")


    @withHeal
    def commit(self):
        self.__dbConnection.commit()
        logging.debug("Commited transaction to database")

    @withHeal
    def rollback(self):
        self.__dbConnection.rollback()
        logging.debug("Uncommitted changes to database rolled back")
    


                

    def __enter__(self):
        logging.debug("DBManager.__enter__")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        logging.debug("DBManager.__exit__")


        