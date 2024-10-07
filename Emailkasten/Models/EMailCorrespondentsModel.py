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
from ..constants import ParsedMailKeys
from .EMailModel import EMailModel
from .CorrespondentModel import CorrespondentModel

class EMailCorrespondentsModel(models.Model):
    email = models.ForeignKey(EMailModel, related_name="emailcorrespondents", on_delete=models.CASCADE)
    correspondent = models.ForeignKey(CorrespondentModel, related_name="correspondentemails", on_delete=models.CASCADE)
    MENTIONTYPES = dict(ParsedMailKeys.Correspondent())
    mention = models.CharField(choices=MENTIONTYPES, max_length=30)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"EMail-Correspondent connection from email {self.email} to correspondent {self.correspondent} with mention {self.mention}"
    
    class Meta:
        unique_together = ('email', 'correspondent', 'mention')
        db_table = "email_correspondents"
