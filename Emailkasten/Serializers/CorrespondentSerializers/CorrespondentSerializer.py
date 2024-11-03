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

from ...Models.CorrespondentModel import CorrespondentModel
from ...Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ..EMailCorrespondentsSerializers.CorrespondentEMailSerializer import \
    CorrespondentEMailSerializer


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
