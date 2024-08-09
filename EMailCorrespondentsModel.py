from django.db import models
from EMailModel import EMailModel
from CorrespondentModel import CorrespondentModel

class EMailCorrespondentsModel(models.Model):
    emailID = models.ForeignKey(EMailModel, related_name="emails", on_delete=models.CASCADE)
    correspondentID = models.ForeignKey(CorrespondentModel, related_name="correspondents", on_delete=models.CASCADE)
    mention = models.TextChoices("TO", "FROM", "CC", "BCC", non_null=True)
    models.UniqueConstraint(emailID, correspondentID, mention)