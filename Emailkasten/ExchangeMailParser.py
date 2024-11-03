# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import exchangelib



class ExchangeMailParser:

    def __init__(self, mailToParse):
        if isinstance(mailToParse, exchangelib.Message):
            self.mailMessage = mailToParse
        else: raise TypeError('Mail is no in Message format!')

    def parseFrom(self):    
        decodedSender = self.mailMessage.sender
        return (decodedSender.name, decodedSender.email_address)

    def parseTo(self):
        return [(recipient.name, recipient.email_address) for recipient in self.mailMessage.to_recipients]
        
    def parseBcc(self):
        recipients = [(recipient.name, recipient.email_address) for recipient in self.mailMessage.bcc_recipients]
        return recipients
    
    def parseCc(self):
        recipients = [(recipient.name, recipient.email_address) for recipient in self.mailMessage.cc_recipients]
        return recipients
    
    def parseDate(self):
        return str(self.mailMessage.datetime_received)
        
    def parseBody(self):
        return str(self.mailMessage.text_body)
        
    def parseSubject(self):
        return self.decodeHeader(self.mailMessage.subject)
