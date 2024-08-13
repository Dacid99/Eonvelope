from django.db import models
from .EMailModel import EMailModel
from .CorrespondentModel import CorrespondentModel

class EMailCorrespondentsModel(models.Model):
    email = models.ForeignKey(EMailModel, related_name="emails", on_delete=models.CASCADE)
    correspondent = models.ForeignKey(CorrespondentModel, related_name="correspondents", on_delete=models.CASCADE)
    mentionTypes = {"TO" : "To", "FROM" : "From", "CC" : "Cc", "BCC" : "Bcc"}
    mention = models.CharField(choices=mentionTypes, max_length=10)

    def __str__(self):
        return f"EMail-Correspondent connection from email {self.email} to correspondent {self.correspondent} with mention {self.mention}"
    
    class Meta:
        unique_together = ('email', 'correspondent', 'mention')
        db_table = "email_correspondents"
