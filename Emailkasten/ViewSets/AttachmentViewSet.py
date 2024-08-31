from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from ..Models.AttachmentModel import AttachmentModel
from ..Serializers import AttachmentSerializer
from ..Filters.AttachmentsFilter import AttachmentFilter
import os

class AttachmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AttachmentModel.objects.all()
    serializer_class = AttachmentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = AttachmentFilter
    ordering_fields = ['file_name', 'datasize', 'email__datetime', 'created']
    ordering = ['id']

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        attachment = self.get_object()
        fileName = attachment.file_name
        filePath = attachment.file_path

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response