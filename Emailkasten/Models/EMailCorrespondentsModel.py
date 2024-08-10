from django.db import models
from EMailModel import EMailModel
from CorrespondentModel import CorrespondentModel

class EMailCorrespondentsModel(models.Model):
    email_id = models.ForeignKey(EMailModel, related_name="emails", on_delete=models.CASCADE)
    correspondent_id = models.ForeignKey(CorrespondentModel, related_name="correspondents", on_delete=models.CASCADE)
    mention = models.TextChoices("TO", "FROM", "CC", "BCC", non_null=True)

    def __str__(self):
        return f"EMail-Correspondent connection from email {self.email_id} to correspondent {self.correspondent_id} with mention {self.mention}"
    
    class Meta:
        unique_together = ('email_id', 'correspondent_id', 'mention')
        db_table = "correspondents"