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
from ...Models.MailboxModel import MailboxModel
from ..DaemonSerializers.DaemonSerializer import DaemonSerializer
        

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

    def validate_fetching_criterion(self, value):
        if self.instance and value not in self.instance.getAvailableFetchingCriteria():
            raise serializers.ValidationError("Fetching criterion not available for this mailbox!")
    