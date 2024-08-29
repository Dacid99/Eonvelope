from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from ..Models.EMailModel import EMailModel
from ..Serializers import EMailSerializer
from ..Filters.EMailFilter import EMailFilter
import os

class EMailViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EMailModel.objects.all()
    serializer_class = EMailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = EMailFilter

    ALLOWED_SORT_FIELDS = ['datetime', 'email_subject', 'datasize']

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort', None)
        if sort_by:
            sort_fields = sort_by.split(',')
            for field in sort_fields:
                    if field.startswith('-'):
                        field_name = field[1:]  # Remove the leading '-'
                        if field_name in self.ALLOWED_SORT_FIELDS:
                            queryset = queryset.order_by(field)  # Descending order
                        else:
                            raise ValidationError(f"Invalid sort field: {field_name}")
                    else:
                        if field in self.ALLOWED_SORT_FIELDS:
                            queryset = queryset.order_by(field)  # Ascending order
                        else:
                            raise ValidationError(f"Invalid sort field: {field}")

        return queryset

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        email = self.get_object()
        fileName = email.message_id
        filePath = email.eml_filepath

        if not os.path.exists(filePath):
            raise Http404("Attachment file not found")
        
        response = FileResponse(open(filePath, 'rb'), as_attachment=True, filename=fileName)
        return response
    

    @action(detail=True, methods=['post'], url_path='toggle_favorite')
    def toggle_favorite(self, request, pk=None):
        email = self.get_object()
        email.is_favorite = not email.is_favorite
        email.save()
        return Response({'status': 'Email marked as favorite'})
    
    
    @action(detail=False, methods=['get'], url_path='favorites')
    def favorites(self, request):
        favoriteEmails = EMailModel.objects.filter(is_favorite=True)
        serializer = self.get_serializer(favoriteEmails, many=True)
        return Response(serializer.data)