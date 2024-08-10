from rest_framework import viewsets
from EMailModel import EMailModel

class EMailViewSet(viewsets.ModelViewSet):
    class Meta:
        model = EMailModel
        fields = '__all__'