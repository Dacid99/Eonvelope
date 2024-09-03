from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers import CorrespondentSerializer, SimpleCorrespondentSerializer
from ..Filters.CorrespondentFilter import CorrespondentFilter

class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CorrespondentFilter
    ordering_fields = ['email_name', 'email_address', 'created']
    ordering = ['id']

    def get_queryset(self):
        return CorrespondentModel.objects.filter(correspondentemails__email__account__user = self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleCorrespondentSerializer
        return super().get_serializer_class()