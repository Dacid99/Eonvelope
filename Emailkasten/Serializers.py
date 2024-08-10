from rest_framework import serializers

from AccountModel import AccountModel
from EmailModel import EmailModel
from CorrespondentModel import CorrespondentModel
from EMailCorrespondentsModel import EMailCorrespondentsModel
from AttachmentModel import AttachmentModel

class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = AccountModel
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