'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
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

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)

        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        
        if 'is_staff' in validated_data and validated_data['is_staff']:
            request = self.context.get('request')
            if request.user.is_staff:
                instance.is_staff = validated_data['is_staff']
            else:
                raise ValidationError({"detail": "You do not have permissions to perform this action."})  # default permissions message to avoid giving clues to attackers
        
        instance.save()
        return instance
    

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
        
    def update(self, instance, validated_data):
        daemonData = validated_data.pop('daemon', None)
        if daemonData:
            daemonInstance = instance.daemon
            for key, value in daemonData.items():
                setattr(daemonInstance, key,value)
            daemonInstance.save()
        
        return super().update(instance, validated_data)
    
        
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
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            correspondentemails = EMailCorrespondentsModel.objects.filter(correspondent=object, email__account__user=user).distinct()
            return CorrespondentEMailSerializer(correspondentemails, many=True, read_only=True).data
        else:
            return None

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentModel
        exclude = ['file_path']


class EMailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    correspondents = serializers.SerializerMethodField()

    class Meta:
        model = EMailModel
        exclude = ['eml_filepath', 'prerender_filepath']
        
    def get_correspondents(self, object):
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            emailcorrespondents = EMailCorrespondentsModel.objects.filter(email=object, email__account__user=user).distinct()
            return EMailCorrespondentSerializer(emailcorrespondents, many=True, read_only=True).data
        else:
            return None