from django.db import models
from FileManager import FileManager
from EMailModel import EMailModel

class AttachmentModel(models.Model):
    fileName = models.CharField(max_length=255)
    filePath = models.FilePathField(
        path=FileManager.attachmentDirectoryPath,
        recursive=True, 
        not_null=True,
        blank=True,  
        unique=True)
    emailID = models.ForeignKey(EMailModel, related_name="emails", on_delete=models.CASCADE)

    def __str__(self):
        return f"Attachment {self.fileName}"