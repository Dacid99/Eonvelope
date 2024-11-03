# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


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
    
