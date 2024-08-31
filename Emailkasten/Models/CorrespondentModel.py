from django.db import models

class CorrespondentModel(models.Model):
    email_name = models.CharField(max_length=255, blank=True)
    email_address = models.CharField(max_length=255, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Correspondent with address {self.email_address}"

    class Meta:
        db_table = "correspondents"