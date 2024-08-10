import exchangelib
from ExchangeMailParser import ExchangeMailParser

class ExchangeFetcher:
    protocol = "EXCHANGE"
    
    def __init__(self, username, password, primary_smtp_address=None, server='outlook.office365.com', fullname=None, access_type=exchangelib.DELEGATE, autodiscover=True, locale=None, default_timezone=None):
        self.__credentials = exchangelib.Credentials(username, password)
        self.__config = exchangelib.Configuration(server=server, credentials=self.__credentials)
        
        self.__mailhost = exchangelib.Account(
            primary_smtp_address=primary_smtp_address,fullname=fullname,access_type=access_type,autodiscover=autodiscover,locale=locale,default_timezone=default_timezone
            )
        
    def fetchAllAndPrint(self):
        for message in self.__mailhost.inbox.all().order_by('-datetime_received')[:10]:
            mailParser = ExchangeMailParser(message)
            print(mailParser.parseFrom())


    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")