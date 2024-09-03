from rest_framework import serializers
from django.contrib.auth.models import User
from .Models.AccountModel import AccountModel
from .Models.MailboxModel import MailboxModel
from .Models.DaemonModel import DaemonModel
from .Models.EMailModel import EMailModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from .Models.AttachmentModel import AttachmentModel
from .Models.ConfigurationModel import ConfigurationModel

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'is_staff']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False) 
        )
        return user


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationModel
        fields = '__all__'
        read_only_fields = ['created', 'updated']
        
        
class DaemonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DaemonModel
        exclude = ['mailbox']
        read_only_fields = ['is_running', 'created', 'updated']


class MailboxWithDaemonSerializer(serializers.ModelSerializer):
    daemon = DaemonSerializer()
    
    class Meta:
        model = MailboxModel
        fields = '__all__'
        read_only_fields = ['name', 'account', 'created', 'updated']
        
        
class MailboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = MailboxModel
        fields = '__all__'
        read_only_fields = ['name', 'account', 'created', 'updated']


class AccountSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, write_only=True)
    mail_address = serializers.EmailField()
    mailboxes = MailboxSerializer(many=True, read_only=True)

    class Meta:
        model = AccountModel
        exclude = ['user']
        read_only_fields = ['is_healthy', 'created', 'updated']

    def validate_mail_address(self, value):
        return value.lower()
    

class SimpleCorrespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CorrespondentModel
        fields = '__all__'


class SimpleEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EMailModel
        exclude = ['eml_filepath']


class EMailCorrespondentSerializer(serializers.ModelSerializer):
    correspondent = SimpleCorrespondentSerializer()
    
    class Meta:
        model = EMailCorrespondentsModel
        fields = ['correspondent', 'mention']


class CorrespondentEMailSerializer(serializers.ModelSerializer):
    email = SimpleEmailSerializer()

    class Meta:
        model = EMailCorrespondentsModel
        fields = ['email', 'mention']


class CorrespondentSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()

    class Meta:
        model = CorrespondentModel
        fields = '__all__'

    def get_emails(self, object):
        correspondentemails = EMailCorrespondentsModel.objects.filter(correspondent=object)
        return CorrespondentEMailSerializer(correspondentemails, many=True, read_only=True).data
    

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentModel
        exclude = ['file_path']


class EMailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    correspondents = serializers.SerializerMethodField()

    class Meta:
        model = EMailModel
        exclude = ['eml_filepath']
        
    def get_correspondents(self, object):
        emailcorrespondents = EMailCorrespondentsModel.objects.filter(email=object)
        return EMailCorrespondentSerializer(emailcorrespondents, many=True, read_only=True).data
