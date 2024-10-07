'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import poplib

from .. import constants
import logging

class POP3Fetcher: 

    PROTOCOL = constants.MailFetchingProtocols.POP3_SSL

    def __init__(self, account):
        self.account = account

        self.logger = logging.getLogger(__name__)
        
        try:
            self.connectToHost()
            self.login()
        except poplib.error_proto as e:
            self.logger.error(f"Failed connecting to {str(self.account)}!", exc_info=True)
            self._mailhost = None
            self.account.is_healthy = False
            self.account.save()
            self.logger.info(f"Marked {str(self.account)} as unhealthy")


    def connectToHost(self):
        self.logger.debug(f"Connecting to {str(self.account)} ...")
        self._mailhost = poplib.POP3(host=self.account.mail_host, port=self.account.mail_host_port, timeout=None)
        self.logger.debug("Success")

    def login(self):
        self.logger.debug(f"Logging into {str(self.account)} ...")
        self._mailhost.user(self.account.mail_account)
        self._mailhost.pass_(self.account.password)
        self.logger.info(f"Successfully logged into {str(self.account)}.")

    def close(self):
        self.logger.debug(f"Closing connection to {str(self.account)} ...")
        if self._mailhost:
            try:
                self._mailhost.quit()
                self.logger.info(f"Gracefully closed connection to {str(self.account)}.")
            except poplib.error_proto:
                self.logger.error(f"Failed to close connection to {str(self.account)}!", exc_info=True)

    def __bool__(self):
        self.logger.debug(f"Testing connection to {str(self.account)}")
        return self._mailhost is not None
    
    @staticmethod
    def test(account):
        with POP3Fetcher(account) as pop3Fetcher:
            return bool(pop3Fetcher)


    def fetchAll(self):
        self.logger.debug(f"Fetching all messages in {str(self.account)} ...")
        try:
            status, messageNumbersList, _ = self._mailhost.list()
            if status != b'+OK':
                self.logger.error(f"Bad response trying to fetch mails, response {status}")
                return []

            messageCount = len(messageNumbersList)
            self.logger.debug(f"Found {messageCount} messages in {str(self.account)}.")
            mailDataList = []
            for number in range(messageCount):
                status, messageData, _ = self._mailhost.retr(number + 1)
                if status != b'+OK':
                    self.logger.error(f"Bad response trying to fetch mail {number}, response {status}")
                    continue
                    
                fullMessage = b'\n'.join(messageData)
                mailDataList.append(fullMessage)

            self.logger.debug(f"Successfully fetched all messages in {str(self.account)}.")
            return mailDataList
                
        except poplib.error_proto as e:
            self.logger.error(f"Failed to fetch all messages in {str(self.account)}!", exc_info=True)
            return []

    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")
        self.close()
