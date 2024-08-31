import django_filters
from ..Models.AccountModel import AccountModel

class AccountFilter(django_filters.FilterSet):

    class Meta:
        model = AccountModel
        fields = {
            'mail_address': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'mail_host': ['icontains', 'contains', 'exact', 'iexact', 'startswith', 'istartswith', 'endswith', 'iendswith', 'regex', 'iregex', 'in'],
            'mail_host_port': ['exact', 'lte', 'gte', 'lt', 'gt', 'in'],
            'protocol': ['icontains', 'iexact', 'in'],
            'is_healthy': ['exact'],
            'created': ['lte', 'gte'],
            'updated': ['lte', 'gte']
        }