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
from .. import constants
from .AccountModel import AccountModel


class EMailModel(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    datetime = models.DateTimeField()
    email_subject = models.CharField(max_length=255)
    bodytext = models.TextField()
    datasize = models.IntegerField()
    eml_filepath = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=r".*\.eml$", 
        null=True
    )
    prerender_filepath = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=rf".*{constants.StorageConfiguration.PRERENDER_BASENAME}\.{constants.StorageConfiguration.PRERENDER_IMAGETYPE}$", 
        null=True
    )
    is_favorite = models.BooleanField(default=False)
    correspondents = models.ManyToManyField('CorrespondentModel', through='EMailCorrespondentsModel', related_name='emails')
    account = models.ForeignKey(AccountModel, related_name="emails", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.datetime} with subject {self.email_subject}"

    class Meta:
        db_table = "emails"
