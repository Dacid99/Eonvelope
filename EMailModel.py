from django.db import models
from FileManager import FileManager

class EMailModel(models.Model):
    message_id = models.CharField(max_length=255, unique=True, not_null=True)
    date_received = models.DateTimeField(not_null=True)
    email_subject = models.CharField(max_length=255, not_null=True)
    bodytext = models.TextField(not_null=True)
    eml_filepath = models.FilePathField(
        path=FileManager.emlDirectoryPath, 
        recursive=True, 
        match='.*\.eml$', 
        blank=True, 
        not_null=True
    )

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.date_received} with subject {self.email_subject}"

    class Meta:
        db_table = "emails"