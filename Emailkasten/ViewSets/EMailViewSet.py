from rest_framework import viewsets
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from ..Models.EMailModel import EMailModel
from ..Serializers import EMailSerializer
import os

class EMailViewSet(viewsets.ModelViewSet):
    queryset = EMailModel.objects.all()
    serializer_class = EMailSerializer

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        email = self.get_object()
        fileName = email.message_id
        filePath = email.eml_filepath

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response