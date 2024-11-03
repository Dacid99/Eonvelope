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

from django.db import models

from .. import constants
from .AccountModel import AccountModel
from .MailingListModel import MailingListModel


class EMailModel(models.Model):
    """Database model for an email."""

    message_id = models.CharField(max_length=255)
    """The messageID header of the mail. Unique together with `account`."""

    datetime = models.DateTimeField()
    """The Date header of the mail."""

    email_subject = models.CharField(max_length=255)
    """The subject header of the mail."""

    bodytext = models.TextField()
    """The bodytext of the mail."""

    inReplyTo = models.ForeignKey('self', null=True, related_name='replies', on_delete=models.SET_NULL)
    """The mail that this mail is a response to. Can bbe null. Deletion of that `inReplyTo` sets this field to NULL."""

    datasize = models.IntegerField()
    """The bytes size of the mail."""

    eml_filepath = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=r".*\.eml$", 
        null=True
    )
    """The path where the mail is stored in .eml format.
    Can be null if the mail has not been saved.
    Must contain :attr:`Emailkasten.constants.StorageConfiguration.STORAGE_PATH` and end on .eml ."""
    
    prerender_filepath = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=rf".*\.{constants.StorageConfiguration.PRERENDER_IMAGETYPE}$", 
        null=True
    )
    """The path where the prerender image of the mail is stored.
    Can be null if the prerendering process was no successful.
    Must contain :attr:`Emailkasten.constants.StorageConfiguration.STORAGE_PATH` and end on :attr:`Emailkasten.constants.StorageConfiguration.PRERENDER_IMAGETYPE`."""
    
    is_favorite = models.BooleanField(default=False)
    """Flags favorite mails. False by default."""
    
    correspondents = models.ManyToManyField('CorrespondentModel', through='EMailCorrespondentsModel', related_name='emails')
    """The correspondents that are mentioned in this mail. Bridges through :class:`Emailkasten.Models.EMailCorrespondentsModel`."""
    
    mailinglist = models.ForeignKey(MailingListModel, null=True, related_name='emails', on_delete=models.CASCADE)
    """The mailinglist that this mail has been sent from. Can be null. Deletion of that `mailinglist` deletes this mail."""
    
    account = models.ForeignKey(AccountModel, related_name="emails", on_delete=models.CASCADE)
    """The account that this mail has been found in. Unique together with `message_id`. Deletion of that `account` deletes this mail."""
    
    comments = models.CharField(max_length=255, null=True)
    """The comments header of this mail. Can be null."""
    
    keywords = models.CharField(max_length=255, null=True)
    """The keywords header of this mail. Can be null."""
    
    importance = models.CharField(max_length=255, null=True)
    """The importance header of this mail. Can be null."""
    
    priority = models.CharField(max_length=255, null=True)
    """The priority header of this mail. Can be null."""
    
    precedence = models.CharField(max_length=255, null=True)
    """The precedence header of this mail. Can be null."""
    
    received = models.TextField(null=True)
    """The received header of this mail. Can be null."""
    
    user_agent = models.CharField(max_length=255, null=True)
    """The user_agent header of this mail. Can be null."""
    
    auto_submitted = models.CharField(max_length=255, null=True)
    """The auto_submitted header of this mail. Can be null."""
    
    content_type = models.CharField(max_length=255, null=True)
    """The content_type header of this mail. Can be null."""
    
    content_language = models.CharField(max_length=255, null=True)
    """The content_language header of this mail. Can be null."""
    
    content_location = models.CharField(max_length=255, null=True)
    """The content_location header of this mail. Can be null."""
    
    x_priority = models.CharField(max_length=255, null=True)
    """The x_priority header of this mail. Can be null."""
    
    x_originated_client = models.CharField(max_length=255, null=True)
    """The x_originated_client header of this mail. Can be null."""
    
    x_spam = models.CharField(max_length=255, null=True) 
    """The x_spam header of this mail. Can be null."""
    
    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""
    

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.datetime} with subject {self.email_subject}"

    class Meta:
        db_table = "emails"
        """The name of the database table for the emails."""

        unique_together = ("message_id", "account")
        """`message_id` and `account` in combination are unique."""