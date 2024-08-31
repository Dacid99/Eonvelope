import django_filters
from ..Models.CorrespondentModel import CorrespondentModel

class CorrespondentFilter(django_filters.FilterSet):
    mention__iexact = django_filters.CharFilter(field_name='correspondentemails__mention', lookup_expr='iexact')

    class Meta:
        model = CorrespondentModel
        fields = {
            'email_name': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'email_address': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'created': ['lte', 'gte']
        }