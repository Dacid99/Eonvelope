from django.db import models
from .. import constants
from .AccountModel import AccountModel

class EMailModel(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    datetime = models.DateTimeField()
    email_subject = models.CharField(max_length=255)
    bodytext = models.TextField()
    datasize = models.IntegerField()
    eml_filepath = models.FilePathField(
        path=constants.StorageConfiguration.STORAGE_PATH,
        max_length=255, 
        recursive=True, 
        match=r".*\.eml$", 
        null=True
    )
    is_favorite = models.BooleanField(default=False)
    account = models.ForeignKey(AccountModel, related_name="in_account", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Email with ID {self.message_id}, received on {self.datetime} with subject {self.email_subject}"

    class Meta:
        db_table = "emails"
