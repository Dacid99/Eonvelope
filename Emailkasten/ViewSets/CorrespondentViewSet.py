from rest_framework import viewsets
from CorrespondentModel import CorrespondentModel

class CorrespondentViewSet(viewsets.ModelViewSet):
    class Meta:
        model = CorrespondentModel
        fields = '__all__'