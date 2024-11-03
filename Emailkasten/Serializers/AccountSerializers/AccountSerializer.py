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

from rest_framework import serializers

from ...Models.AccountModel import AccountModel
from ..MailboxSerializers.MailboxSerializer import MailboxSerializer


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
    