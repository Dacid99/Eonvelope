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
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..Models.AccountModel import AccountModel
from ..Models.AttachmentModel import AttachmentModel
from ..Models.CorrespondentModel import CorrespondentModel
from ..Models.EMailModel import EMailModel
from ..Models.ImageModel import ImageModel


class DatabaseStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            email_count = EMailModel.objects.filter(account__user = request.user).count()
            correspondent_count = CorrespondentModel.objects.filter(emails__account__user = request.user).distinct().count()
            attachment_count = AttachmentModel.objects.filter(email__account__user = request.user).count()
            images_count = ImageModel.objects.filter(email__account__user = request.user).count()
            account_count = AccountModel.objects.filter(user = request.user).count()

            data = {
                'email_count': email_count,
                'correspondent_count': correspondent_count,
                'attachment_count': attachment_count,
                'images_count': images_count,
                'account_count': account_count,
            }
            return Response(data)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)