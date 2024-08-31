from django.db import models
from .EMailModel import EMailModel
from .. import constants

class AttachmentModel(models.Model):
    file_name = models.CharField(max_length=255)
    file_path = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=511,
        recursive=True,
        unique=True,
        null=True)
    datasize = models.IntegerField()
    email = models.ForeignKey(EMailModel, related_name="attachments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment {self.file_name}"

    class Meta:
        db_table = "attachments"
