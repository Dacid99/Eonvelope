import exchangelib
from ExchangeMailParser import ExchangeMailParser

class ExchangeFetcher:
    def __init__(self, username, password, server='outlook.office365.com', primary_smtp_address=None, fullname=None, access_type=None, autodiscover=False, config=None, locale=None, default_timezone=None):
        self.__credentials = exchangelib.Credentials(username, password)
        self.__config = exchangelib.Configuration(server=server, credentials=self.__credentials)
        self.__mailhost = exchangelib.Account(primary_smtp_address,
                        fullname,
                        access_type,
                        autodiscover,
                        self.__config,
                        locale,
                        default_timezone)
        
    def fetchAllAndPrint(self):
        for message in self.__mailhost.inbox.all().order_by('-datetime_received')[:10]:
            print(ExchangeMailParser.parseFrom(message))