from rest_framework import viewsets
from EMailCorrespondentsModel import EMailCorrespondentsModel

class EMailCorrespondentsViewSet(viewsets.ModelViewSet):
    class Meta:
        model = EMailCorrespondentsModel
        fields = '__all__'