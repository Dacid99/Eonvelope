from rest_framework import serializers

from .Models.AccountModel import AccountModel
from .Models.MailboxModel import MailboxModel
from .Models.EMailModel import EMailModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .Models.AttachmentModel import AttachmentModel

class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = AccountModel
        fields = '__all__'

class MailboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailboxModel
        fields = '__all__'

class EMailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailModel
        fields = '__all__'


class CorrespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrespondentModel
        fields = '__all__'


class EMailCorrespondentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailCorrespondentsModel
        fields = '__all__'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentModel
        fields = '__all__'