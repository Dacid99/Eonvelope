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
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..Filters.MailingListFilter import MailingListFilter
from ..Models.MailingListModel import MailingListModel
from ..Serializers.MailingListSerializers.MailingListSerializer import \
    MailingListSerializer


class MailingListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MailingListModel.objects.all()
    serializer_class = MailingListSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = MailingListFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['list_id', 'list_owner', 'list_subscribe', 'list_unsubscribe', 'list_post', 'list_help', 'list_archive', 'correspondent__email_name', 'correspondent__email_address', 'created', 'updated']
    ordering = ['id']

    def get_queryset(self):
        return MailingListModel.objects.filter(correspondent__emails__account__user = self.request.user).distinct()
    
    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except MailingListModel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        mailinglist = self.get_object()
        mailinglist.is_favorite = not mailinglist.is_favorite
        mailinglist.save()
        return Response({'status': 'Mailinglist marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteMailinglists = MailingListModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteMailinglists, many=True)
        return Response(serializer.data)