from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from ..Models.CorrespondentModel import CorrespondentModel
from ..Serializers import CorrespondentSerializer
from ..Filters.CorrespondentFilter import CorrespondentFilter

class CorrespondentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CorrespondentModel.objects.all()
    serializer_class = CorrespondentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CorrespondentFilter

    ALLOWED_SORT_FIELDS = ['email_name', 'email_address']

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