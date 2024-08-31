import django_filters
from ..Models.CorrespondentModel import CorrespondentModel

class CorrespondentFilter(django_filters.FilterSet):
    mention__exact = django_filters.CharFilter(field_name='correspondentemails__mention', lookup_expr='exact')

    class Meta:
        model = CorrespondentModel
        fields = {
            'email_name': ['icontains', 'contains', 'exact'],
            'email_address': ['icontains', 'contains', 'exact'],
            'created': ['lte', 'gte']
        }