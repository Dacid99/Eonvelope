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

from django.db import models
from django.contrib.auth.models import User
from .. import constants

class AccountModel(models.Model):
    mail_address = models.EmailField(max_length=255)
    password = models.CharField(max_length=255)
    mail_host = models.CharField(max_length=255)
    mail_host_port = models.IntegerField(null=True)
    PROTOCOL_CHOICES = {
        constants.MailFetchingProtocols.IMAP : "IMAP", 
        constants.MailFetchingProtocols.IMAP_SSL : "IMAP SSL",
        constants.MailFetchingProtocols.POP3 : "POP3",
        constants.MailFetchingProtocols.POP3_SSL : "POP3 SSL",
        constants.MailFetchingProtocols.EXCHANGE : "Exchange"
    }
    protocol = models.CharField(choices=PROTOCOL_CHOICES, max_length=10)
    is_healthy = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='accounts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Account {self.mail_address} at host {self.mail_host}:{self.mail_host_port} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"
        unique_together = ("mail_address", "user")


