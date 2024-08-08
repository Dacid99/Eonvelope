from django.db import models

class EMailModel(models.Model):
    messageID = models.CharField(max_length=255, unique=True, not_null=True)
    dateReceived = models.DateTimeField(not_null=True)
    bodyText = models.TextField(not_null=True)
    emlFile = models.FilePathField(
        path='eml_files/', 
        recursive=True, 
        match='.*\.eml$', 
        blank=True, 
        not_null=True
    )

    def __str__(self):
        return f"Email with ID {self.messageID}, received on {self.dateReceived} with subject {self.subject}"