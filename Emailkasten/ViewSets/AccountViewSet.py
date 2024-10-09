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

from rest_framework import viewsets, status
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError
from django_filters.rest_framework import DjangoFilterBackend
from ..Models.AccountModel import AccountModel
from ..Filters.AccountFilter import AccountFilter
from ..Serializers.AccountSerializers.AccountSerializer import AccountSerializer
from ..mailProcessing import testAccount, scanMailboxes


class AccountViewSet(viewsets.ModelViewSet):
    queryset = AccountModel.objects.all()
    serializer_class = AccountSerializer
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    filterset_class = AccountFilter
    permission_classes = [IsAuthenticated]
    ordering_fields = ['mail_address', 'mail_host', 'protocol', 'created', 'updated']
    ordering = ['id']


    def get_queryset(self):
        return AccountModel.objects.filter(user = self.request.user)


    def perform_create(self, serializer):
        try:
            serializer.save(user = self.request.user)
        except IntegrityError as e:
            return Response({'detail': 'This account already exists!'}, status=status.HTTP_500)
        
        
    @action(detail=True, methods=['post'])
    def scan_mailboxes(self, request, pk=None):
        account = self.get_object()
        mailboxesList = scanMailboxes(account)
        
        return Response({'status': 'Scanned for mailboxes', 'account': account.mail_address, 'found mailboxes': mailboxesList})
    
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        account = self.get_object()
        result = testAccount(account)
        return Response({'status': 'Tested mailaccount', 'account': account.mail_address, 'result': result})

