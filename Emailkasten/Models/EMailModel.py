from django.db import models
from ..FileManager import FileManager

class EMailModel(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    date_received = models.DateTimeField()
    email_subject = models.CharField(max_length=255)
    bodytext = models.TextField()
    datasize = models.IntegerField()
    eml_filepath = models.FilePathField(
        path=FileManager.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=r".*\.eml$", 
        null=True
    )

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.date_received} with subject {self.email_subject}"

    class Meta:
        db_table = "emails"
