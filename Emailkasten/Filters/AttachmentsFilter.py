import django_filters
from ..Models.AttachmentModel import AttachmentModel

class AttachmentFilter(django_filters.FilterSet):
    datetime__lte = django_filters.DateTimeFilter(field_name='email__datetime', lookup_expr='lte')
    datetime__gte = django_filters.DateTimeFilter(field_name='email__datetime', lookup_expr='gte')

    class Meta:
        model = AttachmentModel
        fields = {
            'file_name': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'datasize': ['lte', 'gte', 'lt', 'gt', 'exact', 'in'],
            'created': ['lte', 'gte']
        }