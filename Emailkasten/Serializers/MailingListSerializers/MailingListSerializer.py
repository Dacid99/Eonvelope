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

from ...Models.MailingListModel import MailingListModel
from ..EMailSerializers.EMailSerializer import EMailSerializer


class MailingListSerializer(serializers.ModelSerializer):
    emails = EMailSerializer(many=True, read_only=True)
    email_number = serializers.SerializerMethodField()
    
    class Meta:
        model = MailingListModel
        fields = '__all__'

    def get_email_number(self, object):
        number = object.emails.count()
        return number