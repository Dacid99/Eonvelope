# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the :class:`UserSerializer` serializer class."""

from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class UserSerializer(serializers.ModelSerializer):
    """A custom serializer for a :django::class:`contrib.auth.models.User`."""

    password = serializers.CharField(write_only=True)
    """The password field is set to write-only for security reasons."""


    class Meta:
        """Metadata class for the serializer."""

        model = User

        fields = ['username', 'password', 'is_staff']
        """Includes only :django::attr:`contrib.auth.models.User.username`, :attr:`password` and :django::attr:`contrib.auth.models.User.is_staff`."""


    def create(self, validated_data: dict) -> User:
        """Creates a new :django::class:`contrib.auth.models.User` instance with given data.
        Uses :django::func:`contrib.auth.models.UserManager.create_user` to ensure encryption of the password.

        Args:
            validated_data: The validated data to create a new model instance with.

        Returns:
            The newly created model instance.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_staff=validated_data.get('is_staff', False)
        )
        return user


    def update(self, instance: User, validated_data: dict) -> User:
        """Overrides :django::func:`serializers.ModelSerializer.update` to ensure correct encryption of password and proper permission changes.

        Args:
            instance: The model instance to be updated.
            validated_data: The validated data update the model instance with.

        Raises:
            ValidationError: If the user is not staff, and is thus not permitted to make users staff.

        Returns:
            The updated model instance.
        """
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
