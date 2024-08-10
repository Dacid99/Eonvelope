from django.db import models
from FileManager import FileManager
from EMailModel import EMailModel

class AttachmentModel(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.FilePathField(
        path=FileManager.attachmentDirectoryPath,
        recursive=True, 
        not_null=True,
        blank=True,  
        unique=True)
    email_id = models.ForeignKey(EMailModel, related_name="emails", on_delete=models.CASCADE)

    def __str__(self):
        return f"Attachment {self.file_name}"

    class Meta:
        db_table = "attachments"