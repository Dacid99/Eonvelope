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

from ...Models.EMailCorrespondentsModel import EMailCorrespondentsModel
from ...Models.EMailModel import EMailModel
from ..AttachmentSerializers.AttachmentSerializer import AttachmentSerializer
from ..EMailCorrespondentsSerializers.EMailCorrespondentsSerializer import \
    EMailCorrespondentSerializer


class EMailSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    correspondents = serializers.SerializerMethodField()

    class Meta:
        model = EMailModel
        fields = ['message_id', 'datetime', 'email_subject', 'bodytext', 'is_favorite', 'account', 'created', 'updated']
        
    def get_correspondents(self, object):
        request = self.context.get('request')
        user = request.user if request else None
        if user:
            emailcorrespondents = EMailCorrespondentsModel.objects.filter(email=object, email__account__user=user).distinct()
            return EMailCorrespondentSerializer(emailcorrespondents, many=True, read_only=True).data
        else:
            return None