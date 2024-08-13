from django.db import models
from .EMailModel import EMailModel
from ..FileManager import FileManager 

class AttachmentModel(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.FilePathField(
        path=FileManager.attachmentDirectoryPath,
        recursive=True,
        unique=True,
        null=True)
    datasize = models.IntegerField()
    email = models.ForeignKey(EMailModel, related_name="email", on_delete=models.CASCADE)

    def __str__(self):
        return f"Attachment {self.file_name}"

    class Meta:
        db_table = "attachments"
