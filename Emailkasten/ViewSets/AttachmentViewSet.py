from rest_framework import viewsets
from AttchmentModel import AttchmentModel

class AttchmentViewSet(viewsets.ModelViewSet):
    class Meta:
        model = AttchmentModel
        fields = '__all__'