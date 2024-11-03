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

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.CorrespondentFilter import CorrespondentFilter
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers.CorrespondentSerializers.CorrespondentSerializer import \
    CorrespondentSerializer
from ..Serializers.CorrespondentSerializers.SimpleCorrespondentSerializer import \
    SimpleCorrespondentSerializer


class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CorrespondentFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['email_name', 'email_address', 'created']
    ordering = ['id']

    def get_queryset(self):
        return CorrespondentModel.objects.filter(emails__account__user = self.request.user).distinct()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleCorrespondentSerializer
        return super().get_serializer_class()


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        correspondent = self.get_object()
        correspondent.is_favorite = not correspondent.is_favorite
        correspondent.save()
        return Response({'status': 'Correspondent marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteCorrespondents = CorrespondentModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteCorrespondents, many=True)
        return Response(serializer.data)