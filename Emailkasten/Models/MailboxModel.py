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
from rest_framework.decorators import action
from ..constants import MailFetchingCriteria, FetchingConfiguration
from .AccountModel import AccountModel
from ..Fetchers.IMAPFetcher import IMAPFetcher
from ..Fetchers.POP3Fetcher import POP3Fetcher 

class MailboxModel(models.Model):
    name = models.CharField(max_length=255)
    account = models.ForeignKey(AccountModel, related_name="mailboxes", on_delete=models.CASCADE)
    FETCHINGCHOICES = dict(MailFetchingCriteria())
    fetching_criterion = models.CharField(choices=FETCHINGCHOICES, default=MailFetchingCriteria.ALL, max_length=10)
    save_attachments = models.BooleanField(default=FetchingConfiguration.SAVE_ATTACHMENTS_DEFAULT)
    save_images = models.BooleanField(default=FetchingConfiguration.SAVE_IMAGES_DEFAULT)
    save_toEML = models.BooleanField(default=FetchingConfiguration.SAVE_TO_EML_DEFAULT)
    is_favorite = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Mailbox {self.name} of {self.account}"

    def getAvailableFetchingCriteria(self):
        if self.account.protocol.startswith(IMAPFetcher.PROTOCOL):
            availableFetchingOptions = IMAPFetcher.AVAILABLE_FETCHING_CRITERIA
        elif self.account.protocol.startswith(POP3Fetcher.PROTOCOL):
            availableFetchingOptions = POP3Fetcher.AVAILABLE_FETCHING_CRITERIA
        else:
            availableFetchingOptions = []
        return availableFetchingOptions

    class Meta:
        db_table = "mailboxes"
        unique_together = ('name', 'account')

